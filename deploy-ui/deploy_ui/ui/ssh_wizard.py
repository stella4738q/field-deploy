"""SSH 金鑰佈建精靈：產生金鑰 → 密碼連線上傳公鑰 → 驗證免密碼登入。

等效 CLI 的 setup_ssh.sh：含 ~/.ssh/config managed block 更新（本機檔案）。
"""

from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from deploy_ui.models import Host, Site
from deploy_ui.services.ssh_executor import SSHSession
from deploy_ui.services.tasks import Worker
from deploy_ui.ui.terminal_widget import TerminalWidget

KEY_PATH = Path.home() / ".ssh" / "id_ed25519"


def update_ssh_config_block(site: Site, config_path: Path | None = None) -> None:
    """~/.ssh/config 寫入 managed block（備份、清舊塊、追加），與 setup_ssh.sh 等效。"""
    cfg = config_path or (Path.home() / ".ssh" / "config")
    site_tag = site.env.get("SITE_NAME", site.name)
    begin, end = f"# BEGIN {site_tag} deploy-tool", f"# END {site_tag} deploy-tool"

    cfg.parent.mkdir(parents=True, exist_ok=True)
    old = cfg.read_text(encoding="utf-8") if cfg.is_file() else ""
    if old:
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        cfg.with_suffix(f".bak.{ts}").write_text(old, encoding="utf-8")

    lines, skip = [], False
    for ln in old.splitlines():
        if ln.strip() == begin:
            skip = True
            continue
        if ln.strip() == end:
            skip = False
            continue
        if not skip:
            lines.append(ln)

    block = [begin]
    for h in site.hosts:
        block += [
            f"Host {h.name}",
            f"    HostName {h.ssh_host}",
            f"    Port {h.port}",
            f"    User {h.user}",
            "    ServerAliveInterval 30",
        ]
        if h.readonly:
            block.append("    # ⚠ 唯讀主機，只能看，嚴禁改動")
    block.append(end)

    new = "\n".join([*lines, *block]) + "\n"
    cfg.write_text(new, encoding="utf-8")
    cfg.chmod(0o600)


class SshWizardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.site: Site | None = None
        self.worker: Worker | None = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        key_box = QGroupBox("步驟 1：本機金鑰")
        kv = QHBoxLayout(key_box)
        self.key_label = QLabel()
        kv.addWidget(self.key_label, stretch=1)
        self.gen_btn = QPushButton("產生金鑰")
        self.gen_btn.clicked.connect(self._generate_key)
        kv.addWidget(self.gen_btn)
        root.addWidget(key_box)

        host_box = QGroupBox("步驟 2：勾選要佈建的主機（唯讀主機不可選）")
        hv = QVBoxLayout(host_box)
        self.host_list = QListWidget()
        hv.addWidget(self.host_list)
        root.addWidget(host_box)

        pw_box = QGroupBox("步驟 3：SSH 密碼（各台共用，只存在記憶體）")
        pv = QHBoxLayout(pw_box)
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        pv.addWidget(self.pw_edit)
        self.run_btn = QPushButton("開始佈建")
        self.run_btn.clicked.connect(self._start)
        pv.addWidget(self.run_btn)
        root.addWidget(pw_box)

        self.terminal = TerminalWidget()
        root.addWidget(self.terminal, stretch=1)
        self._refresh_key_label()

    def _refresh_key_label(self):
        if KEY_PATH.is_file():
            self.key_label.setText(f"✓ 已有金鑰：{KEY_PATH}")
            self.gen_btn.setEnabled(False)
        else:
            self.key_label.setText(f"尚無金鑰（將建立 {KEY_PATH}）")
            self.gen_btn.setEnabled(True)

    def set_site(self, site: Site) -> None:
        self.site = site
        self.host_list.clear()
        for h in site.hosts:
            li = QListWidgetItem(h.display)
            li.setData(Qt.ItemDataRole.UserRole, h.name)
            if h.readonly:
                li.setFlags(Qt.ItemFlag.NoItemFlags)
            else:
                li.setFlags(li.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                li.setCheckState(Qt.CheckState.Checked)  # 精靈預設全勾
            self.host_list.addItem(li)

    def _generate_key(self):
        try:
            KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(KEY_PATH)],
                check=True, capture_output=True, text=True,
            )
            self.terminal.append_line("", f"✓ 金鑰已建立：{KEY_PATH}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "錯誤", f"ssh-keygen 失敗：{e.stderr}")
        self._refresh_key_label()

    def _checked_hosts(self) -> list[Host]:
        assert self.site is not None
        names = [
            self.host_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.host_list.count())
            if self.host_list.item(i).checkState() == Qt.CheckState.Checked
        ]
        return [h for h in self.site.hosts if h.name in names]

    def _start(self):
        if self.site is None:
            return
        if not KEY_PATH.is_file():
            QMessageBox.warning(self, "提示", "請先產生金鑰")
            return
        hosts = self._checked_hosts()
        if not hosts:
            QMessageBox.warning(self, "提示", "請勾選至少一台主機")
            return
        password = self.pw_edit.text()
        if not password:
            QMessageBox.warning(self, "提示", "請輸入 SSH 密碼")
            return

        pubkey = (KEY_PATH.with_suffix(".pub")).read_text(encoding="utf-8").strip()
        site = self.site

        def job(worker: Worker) -> bool:
            ok_all = True
            # 1. 更新本機 ~/.ssh/config alias
            try:
                update_ssh_config_block(site)
                worker.emit_line("", "✓ ~/.ssh/config alias 已更新（舊檔已備份 .bak.*）")
            except Exception as e:  # noqa: BLE001
                worker.emit_line("", f"✗ 更新 ~/.ssh/config 失敗：{e}")
                ok_all = False
            # 2. 逐台上傳公鑰 + 驗證
            append_cmd = (
                "mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
                f"grep -qxF {_sq(pubkey)} ~/.ssh/authorized_keys 2>/dev/null "
                f"|| echo {_sq(pubkey)} >> ~/.ssh/authorized_keys && "
                "chmod 600 ~/.ssh/authorized_keys"
            )
            for h in hosts:
                if worker.cancelled:
                    return False
                try:
                    worker.emit_line(h.name, "以密碼連線、上傳公鑰…")
                    with SSHSession(h, password=password) as s:
                        r = s.run(append_cmd)
                        if not r.ok:
                            raise RuntimeError(r.output or "寫入 authorized_keys 失敗")
                    with SSHSession(h, key_path=KEY_PATH) as s:
                        r = s.run("echo ok")
                    if r.ok:
                        worker.emit_line(h.name, "✓ 金鑰佈建完成，免密碼登入 OK")
                        worker.emit_step(h.name, "SSH 金鑰佈建", True)
                    else:
                        raise RuntimeError("金鑰驗證失敗")
                except Exception as e:  # noqa: BLE001
                    worker.emit_line(h.name, f"✗ {e}")
                    worker.emit_step(h.name, "SSH 金鑰佈建", False)
                    ok_all = False
            return ok_all

        self.worker = Worker(job)
        self.worker.line.connect(self.terminal.append_line)
        self.worker.done.connect(self._on_done)
        self.run_btn.setEnabled(False)
        self.terminal.append_separator("開始 SSH 佈建")
        self.worker.start()

    def _on_done(self, ok: bool, err: str):
        self.run_btn.setEnabled(True)
        self.terminal.append_separator("✅ 完成" if ok else "⚠ 完成（有失敗）")
        self.worker = None


def _sq(s: str) -> str:
    """單引號 shell quoting。"""
    return "'" + s.replace("'", "'\\''") + "'"
