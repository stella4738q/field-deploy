"""程式部署頁：選案場配置目錄（含 docker-compose.yml）→ 推送到主機 → compose up。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from deploy_ui.models import Site
from deploy_ui.services.catalog import Catalog
from deploy_ui.services.ssh_executor import SSHSession
from deploy_ui.services.tasks import Worker
from deploy_ui.ui.terminal_widget import TerminalWidget

import shlex
import time


class DeployPage(QWidget):
    def __init__(self, catalog: Catalog, parent=None):
        super().__init__(parent)
        self.catalog = catalog
        self.site: Site | None = None
        self.worker: Worker | None = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        sel_box = QGroupBox("部署目標")
        sv = QVBoxLayout(sel_box)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("主機"))
        self.host_combo = QComboBox()
        row1.addWidget(self.host_combo, stretch=1)
        sv.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("配置目錄"))
        self.dir_combo = QComboBox()
        row2.addWidget(self.dir_combo, stretch=1)
        sv.addLayout(row2)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("金鑰"))
        self.key_edit = QLineEdit()
        default_key = Path.home() / ".ssh" / "id_ed25519"
        if default_key.is_file():
            self.key_edit.setText(str(default_key))
        row3.addWidget(self.key_edit, stretch=1)
        row3.addWidget(QLabel("密碼"))
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_edit.setPlaceholderText("sudo／SSH 備用")
        row3.addWidget(self.pw_edit, stretch=1)
        sv.addLayout(row3)
        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("推送並啟動（docker compose up -d）")
        self.run_btn.clicked.connect(self._start)
        btn_row.addStretch(1)
        btn_row.addWidget(self.run_btn)
        sv.addLayout(btn_row)
        root.addWidget(sel_box)

        self.terminal = TerminalWidget()
        root.addWidget(self.terminal, stretch=1)

    def set_site(self, site: Site) -> None:
        self.site = site
        self.host_combo.clear()
        for h in site.writable_hosts():
            self.host_combo.addItem(h.display, h.name)
        self.dir_combo.clear()
        for d in self._compose_dirs(site.path):
            self.dir_combo.addItem(str(d.relative_to(site.path)), str(d))

    @staticmethod
    def _compose_dirs(site_path: Path) -> list[Path]:
        """列出含 docker-compose.yml 的「頂層可部署目錄」（去重：取包含者）。"""
        dirs: set[Path] = set()
        for compose in sorted(site_path.rglob("docker-compose.yml")):
            dirs.add(compose.parent)
        # 若父目錄底下有多個 compose，允許選父目錄一次部署
        parents: set[Path] = set()
        for d in dirs:
            if d.parent != site_path and any(
                other != d and other.is_relative_to(d.parent) for other in dirs
            ):
                parents.add(d.parent)
        return sorted(dirs | parents)

    def _start(self):
        if self.site is None or self.host_combo.currentIndex() < 0:
            return
        if self.dir_combo.currentIndex() < 0:
            QMessageBox.warning(self, "提示", "此案場沒有含 docker-compose.yml 的配置目錄")
            return
        host = self.site.host(self.host_combo.currentData())
        src = Path(self.dir_combo.currentData())
        if host is None or host.readonly:
            QMessageBox.critical(self, "拒絕", "目標主機不可部署")
            return
        composes = list(src.rglob("docker-compose.yml"))
        if QMessageBox.question(
            self, "確認部署",
            f"推送 {src.name}/（含 {len(composes)} 個 docker-compose.yml）到 {host.name}\n"
            f"並逐一 docker compose up -d，確定？",
        ) != QMessageBox.StandardButton.Yes:
            return

        key_path = Path(self.key_edit.text()) if self.key_edit.text().strip() else None
        password = self.pw_edit.text() or None
        payload = self.catalog.payload_dir / "remote_deploy_app.sh"
        remote_base = f"deploy/{src.name}"

        def job(worker: Worker) -> bool:
            with SSHSession(host, key_path=key_path, password=password) as s:
                worker.emit_line(host.name, f"連線成功，開始推送 {src.name}/ …")
                files = [p for p in src.rglob("*") if p.is_file() and ".git" not in p.parts]
                for i, f in enumerate(files, 1):
                    if worker.cancelled:
                        return False
                    rel = f.relative_to(src).as_posix()
                    s.upload_local(f, f"{remote_base}/{rel}")
                    if i % 20 == 0 or i == len(files):
                        worker.emit_line(host.name, f"  已推送 {i}/{len(files)} 個檔案")
                worker.emit_line(host.name, "推送完成，啟動容器…")
                remote_payload = f"/tmp/fd_deploy_app.{int(time.time())}"
                s.upload_local(payload, remote_payload, mode=0o755)
                cmd = (
                    f"bash {shlex.quote(remote_payload)} {shlex.quote(remote_base)}; "
                    f"rc=$?; rm -f {shlex.quote(remote_payload)}; exit $rc"
                )
                result = s.run(
                    cmd,
                    on_line=lambda t: worker.emit_line(host.name, t),
                    sudo_password=password,
                )
                return result.ok

        self.worker = Worker(job)
        self.worker.line.connect(self.terminal.append_line)
        self.worker.done.connect(self._on_done)
        self.run_btn.setEnabled(False)
        self.terminal.append_separator(f"部署 {src.name} → {host.name}")
        self.worker.start()

    def _on_done(self, ok: bool, err: str):
        self.run_btn.setEnabled(True)
        self.terminal.append_separator("✅ 部署完成" if ok else "✗ 部署失敗")
        self.worker = None
