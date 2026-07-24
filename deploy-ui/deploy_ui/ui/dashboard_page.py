"""主機狀態儀表板：連線 / Docker 容器 / 磁碟 / NAS 掛載 / 服務狀態一覽。

只跑唯讀指令（無 sudo），因此唯讀主機也可查看。
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from deploy_ui.models import Host, Site
from deploy_ui.services.ssh_executor import SSHSession
from deploy_ui.services.tasks import Worker

_COLS = ["主機", "連線", "Docker 容器", "磁碟(/)", "NAS 掛載", "服務"]


def _probe_command(mount_point: str) -> str:
    return (
        'echo "==DOCKER=="; docker ps --format "{{.Names}}: {{.Status}}" 2>/dev/null || echo "(docker 不可用)"; '
        'echo "==DISK=="; df -h / | awk \'NR==2{print $3"/"$2" ("$5")"}\'; '
        f'echo "==NAS=="; mountpoint -q {mount_point} 2>/dev/null && echo "✓ 已掛載" || echo "未掛載"; '
        'echo "==SVC=="; for s in keepalived haproxy mongod smbd; do '
        'st=$(systemctl is-active "$s" 2>/dev/null); [ "$st" = "active" ] && echo "$s ✓"; done'
    )


def _parse_probe(output: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("==") and line.endswith("=="):
            current = line.strip("=")
            sections[current] = []
        elif current:
            sections[current].append(line)
    join = lambda k: "\n".join(x for x in sections.get(k, []) if x) or "—"
    return {
        "docker": join("DOCKER"),
        "disk": join("DISK"),
        "nas": join("NAS"),
        "svc": join("SVC").replace("\n", "、") if sections.get("SVC") else "—",
    }


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.site: Site | None = None
        self.worker: Worker | None = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel("金鑰"))
        self.key_edit = QLineEdit()
        default_key = Path.home() / ".ssh" / "id_ed25519"
        if default_key.is_file():
            self.key_edit.setText(str(default_key))
        top.addWidget(self.key_edit, stretch=1)
        top.addWidget(QLabel("密碼"))
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_edit.setPlaceholderText("金鑰不可用時備用")
        top.addWidget(self.pw_edit, stretch=1)
        self.refresh_btn = QPushButton("重新整理")
        self.refresh_btn.clicked.connect(self._refresh)
        top.addWidget(self.refresh_btn)
        root.addLayout(top)

        self.table = QTableWidget(0, len(_COLS))
        self.table.setHorizontalHeaderLabels(_COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setWordWrap(True)
        root.addWidget(self.table, stretch=1)

        self.hint = QLabel("提示：儀表板只執行唯讀指令（docker ps、df、mountpoint、systemctl is-active）")
        root.addWidget(self.hint)

    def set_site(self, site: Site) -> None:
        self.site = site
        self.table.setRowCount(0)
        for h in site.hosts:
            self._ensure_row(h.name)

    def _ensure_row(self, host_name: str) -> int:
        for r in range(self.table.rowCount()):
            if self.table.item(r, 0) and self.table.item(r, 0).text().startswith(host_name):
                return r
        r = self.table.rowCount()
        self.table.insertRow(r)
        assert self.site is not None
        h = self.site.host(host_name)
        label = f"{host_name}（唯讀）" if h and h.readonly else host_name
        self.table.setItem(r, 0, QTableWidgetItem(label))
        for c in range(1, len(_COLS)):
            self.table.setItem(r, c, QTableWidgetItem("…"))
        return r

    def _refresh(self):
        if self.site is None:
            return
        site = self.site
        key_text = self.key_edit.text().strip()
        key_path = Path(key_text) if key_text else None
        password = self.pw_edit.text() or None
        mount_point = site.env.get("NAS_MOUNT_POINT", "/mnt/nas/storage")

        def job(worker: Worker) -> bool:
            for h in site.hosts:
                if worker.cancelled:
                    return False
                row: dict[str, str] = {"host": h.name}
                try:
                    with SSHSession(h, key_path=key_path, password=password,
                                    connect_timeout=6.0) as s:
                        result = s.run(_probe_command(mount_point), timeout=20.0)
                    row["conn"] = "✓ 連線正常"
                    row.update(_parse_probe(result.output))
                except Exception as e:  # noqa: BLE001
                    row["conn"] = f"✗ {type(e).__name__}"
                    row.update({"docker": "—", "disk": "—", "nas": "—", "svc": "—"})
                    worker.emit_line(h.name, f"連線失敗：{e}")
                worker.emit_data(row)
            return True

        self.worker = Worker(job)
        self.worker.data.connect(self._update_row)
        self.worker.done.connect(lambda ok, err: self._on_done())
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("查詢中…")
        self.worker.start()

    def _update_row(self, row: dict):
        r = self._ensure_row(row["host"])
        values = [row.get("conn", "—"), row.get("docker", "—"),
                  row.get("disk", "—"), row.get("nas", "—"), row.get("svc", "—")]
        for c, v in enumerate(values, start=1):
            item = QTableWidgetItem(v)
            if c == 1:
                item.setForeground(
                    Qt.GlobalColor.darkGreen if v.startswith("✓") else Qt.GlobalColor.red
                )
            self.table.setItem(r, c, item)
        self.table.resizeRowsToContents()

    def _on_done(self):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("重新整理")
        self.worker = None
