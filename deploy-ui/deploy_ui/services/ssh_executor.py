"""SSH 執行器：paramiko 包裝，支援即時逐行輸出、sudo、SFTP 上傳。

安全設計（沿用 auto-modbus-reader deploy_tool 的原則）：
- 密碼只存在記憶體，絕不寫入設定檔
- 自管 known_hosts（存於使用者 config 目錄），首連經 confirm callback 確認指紋，
  之後金鑰變更會直接拋錯（防中間人）
- readonly 主機的防護在 catalog 層（這裡是純執行器）
"""

from __future__ import annotations

import base64
import hashlib
import io
import os
import posixpath
import stat
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import paramiko

from deploy_ui.models import Host

SUDO_PROMPT = "__FD_SUDO_PW__"


class SSHAuthError(Exception):
    pass


class SudoAuthError(Exception):
    pass


@dataclass
class CommandResult:
    exit_code: int
    output: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


def config_dir() -> Path:
    """依平台回傳本工具的設定目錄（known_hosts 等）。"""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif os.uname().sysname == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "femc-field-deploy-ui"
    d.mkdir(parents=True, exist_ok=True)
    return d


class _ConfirmPolicy(paramiko.MissingHostKeyPolicy):
    """首次連線：把指紋交給 callback 確認；同意才記入 known_hosts。"""

    def __init__(self, known_hosts: Path, confirm: Callable[[str, str], bool] | None):
        self.known_hosts = known_hosts
        self.confirm = confirm

    def missing_host_key(self, client, hostname, key):
        # OpenSSH 同款指紋格式（SHA256: + base64 去 padding），方便與 ssh-keygen -lf 比對
        digest = hashlib.sha256(key.asbytes()).digest()
        fingerprint = "SHA256:" + base64.b64encode(digest).decode().rstrip("=")
        if self.confirm is not None and not self.confirm(hostname, fingerprint):
            raise SSHAuthError(f"使用者拒絕了 {hostname} 的主機金鑰")
        client.get_host_keys().add(hostname, key.get_name(), key)
        self.known_hosts.parent.mkdir(parents=True, exist_ok=True)
        client.save_host_keys(str(self.known_hosts))


class SSHSession:
    """單一主機的 SSH 連線。用完呼叫 close()（或以 with 使用）。"""

    def __init__(
        self,
        host: Host,
        *,
        key_path: Path | None = None,
        password: str | None = None,
        known_hosts: Path | None = None,
        confirm_hostkey: Callable[[str, str], bool] | None = None,
        connect_timeout: float = 10.0,
    ):
        self.host = host
        self._key_path = key_path
        self._password = password
        self._known_hosts = known_hosts or (config_dir() / "known_hosts")
        self._confirm = confirm_hostkey
        self._timeout = connect_timeout
        self._client: paramiko.SSHClient | None = None

    # ── 連線管理 ─────────────────────────────────────────
    def connect(self) -> None:
        client = paramiko.SSHClient()
        if self._known_hosts.is_file():
            client.load_host_keys(str(self._known_hosts))
        client.set_missing_host_key_policy(
            _ConfirmPolicy(self._known_hosts, self._confirm)
        )
        try:
            client.connect(
                hostname=self.host.ssh_host,
                port=self.host.port,
                username=self.host.user,
                password=self._password,
                key_filename=str(self._key_path) if self._key_path else None,
                timeout=self._timeout,
                allow_agent=True,
                look_for_keys=self._password is None,
            )
        except paramiko.AuthenticationException as e:
            raise SSHAuthError(f"{self.host.name} 認證失敗：{e}") from e
        # 斷網可偵測、避免 UI 永久卡死（load_host_keys 亦讓金鑰變更時
        # paramiko 原生丟 BadHostKeyException，防中間人）
        client.get_transport().set_keepalive(15)
        self._client = client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.close()

    @property
    def client(self) -> paramiko.SSHClient:
        if self._client is None:
            raise RuntimeError("尚未連線（先呼叫 connect()）")
        return self._client

    # ── 指令執行（即時逐行輸出）──────────────────────────
    def run(
        self,
        command: str,
        *,
        on_line: Callable[[str], None] | None = None,
        sudo_password: str | None = None,
        timeout: float | None = None,
        stop: Callable[[], bool] | None = None,
    ) -> CommandResult:
        """執行指令，逐行回呼輸出。

        sudo_password 提供時：配置 pty、先以 `sudo -S -v` 快取憑證
        （密碼經 stdin 送出，不落入命令列），之後指令內的 sudo 不再詢問。
        pty 下強制 TERM=dumb 抑制 apt/docker 的 ANSI 顏色與進度動畫。
        stop() 回傳 True 時中止指令（關閉 channel）並回傳 exit_code=-1。
        """
        use_pty = sudo_password is not None
        if use_pty:
            command = (
                "export TERM=dumb DEBIAN_FRONTEND=noninteractive; "
                f"sudo -S -p '{SUDO_PROMPT}' -v && {command}"
            )

        channel = self.client.get_transport().open_session(timeout=self._timeout)
        if timeout:
            channel.settimeout(timeout)
        if use_pty:
            channel.get_pty(term="dumb", width=200)
        channel.set_combine_stderr(True)
        channel.exec_command(command)

        buf = b""
        lines: list[str] = []
        sent_password = False

        def emit(raw: bytes):
            # pty 進度列以 \r 原地更新：只取最後一段（最終狀態）
            if b"\r" in raw:
                raw = raw.split(b"\r")[-1]
            line = raw.decode("utf-8", errors="replace")
            lines.append(line)
            if on_line is not None:
                on_line(line)

        while True:
            if stop is not None and stop():
                channel.close()
                emit("⚠ 已中止".encode())
                return CommandResult(exit_code=-1, output="\n".join(lines))
            if channel.recv_ready():
                data = channel.recv(4096)
                if not data:
                    break
                buf += data
                # sudo 密碼提示（pty 上不換行，需在殘留 buffer 中偵測）
                if use_pty and SUDO_PROMPT.encode() in buf:
                    if sent_password:
                        channel.close()
                        raise SudoAuthError(f"{self.host.name} 的 sudo 密碼錯誤")
                    channel.send((sudo_password + "\n").encode())
                    sent_password = True
                    buf = buf.replace(SUDO_PROMPT.encode(), b"")
                while b"\n" in buf:
                    raw, buf = buf.split(b"\n", 1)
                    emit(raw)
            elif channel.exit_status_ready():
                break
            else:
                time.sleep(0.05)

        # 沖出殘餘（最後一行可能沒有換行）
        while channel.recv_ready():
            buf += channel.recv(4096)
        if buf.replace(b"\r", b""):
            emit(buf)
        exit_code = channel.recv_exit_status()
        channel.close()
        return CommandResult(exit_code=exit_code, output="\n".join(lines))

    # ── SFTP 上傳 ────────────────────────────────────────
    def upload_content(self, content: str, remote_path: str, mode: int = 0o644) -> None:
        """把字串內容寫到遠端路徑（相對路徑=家目錄起算），自動建立父目錄。"""
        sftp = self.client.open_sftp()
        try:
            self._mkdirs(sftp, posixpath.dirname(remote_path))
            sftp.putfo(io.BytesIO(content.encode("utf-8")), remote_path)
            sftp.chmod(remote_path, mode)
        finally:
            sftp.close()

    def upload_file(self, local: Path, remote_path: str, mode: int = 0o644) -> None:
        self.upload_content(local.read_text(encoding="utf-8"), remote_path, mode)

    def upload_local(self, local: Path, remote_path: str, mode: int = 0o644) -> None:
        """二進位安全的檔案上傳（xlsx 等），自動建立父目錄。"""
        sftp = self.client.open_sftp()
        try:
            self._mkdirs(sftp, posixpath.dirname(remote_path))
            sftp.put(str(local), remote_path)
            sftp.chmod(remote_path, mode)
        finally:
            sftp.close()

    @staticmethod
    def _mkdirs(sftp: paramiko.SFTPClient, directory: str) -> None:
        if not directory or directory in ("/", "."):
            return
        try:
            if stat.S_ISDIR(sftp.stat(directory).st_mode):
                return
        except FileNotFoundError:
            pass
        SSHSession._mkdirs(sftp, posixpath.dirname(directory))
        try:
            sftp.mkdir(directory)
        except OSError:
            pass  # 併發或已存在
