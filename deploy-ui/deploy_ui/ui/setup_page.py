"""環境建置頁：選主機 × 選軟體 → 自動部署，右側即時 terminal + 狀態表。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from deploy_ui.models import Host, Site
from deploy_ui.services.catalog import Catalog, PayloadStep, UploadStep
from deploy_ui.services.runner import PlanRunner
from deploy_ui.services.ssh_executor import SSHSession
from deploy_ui.services.tasks import Worker
from deploy_ui.ui.terminal_widget import TerminalWidget


class SetupPage(QWidget):
    def __init__(self, catalog: Catalog, parent=None):
        super().__init__(parent)
        self.catalog = catalog
        self.site: Site | None = None
        self.worker: Worker | None = None
        self._build_ui()

    # ── UI 佈局 ──────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        # 左側：選擇區
        left = QWidget()
        lv = QVBoxLayout(left)

        host_box = QGroupBox("主機（勾選部署目標）")
        hv = QVBoxLayout(host_box)
        self.host_list = QListWidget()
        hv.addWidget(self.host_list)
        lv.addWidget(host_box)

        sw_box = QGroupBox("軟體（依列出順序執行）")
        sv = QVBoxLayout(sw_box)
        self.sw_list = QListWidget()
        for item in self.catalog.ITEMS:
            li = QListWidgetItem(f"{item.label} — {item.description}")
            li.setData(Qt.ItemDataRole.UserRole, item.key)
            li.setFlags(li.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            li.setCheckState(Qt.CheckState.Unchecked)
            li.setToolTip(item.description)
            self.sw_list.addItem(li)
        sv.addWidget(self.sw_list)
        lv.addWidget(sw_box)

        cred_box = QGroupBox("認證")
        cv = QVBoxLayout(cred_box)
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("金鑰"))
        self.key_edit = QLineEdit()
        default_key = Path.home() / ".ssh" / "id_ed25519"
        if default_key.is_file():
            self.key_edit.setText(str(default_key))
        key_row.addWidget(self.key_edit)
        browse = QPushButton("…")
        browse.setFixedWidth(30)
        browse.clicked.connect(self._pick_key)
        key_row.addWidget(browse)
        cv.addLayout(key_row)
        pw_row = QHBoxLayout()
        pw_row.addWidget(QLabel("密碼"))
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_edit.setPlaceholderText("SSH／sudo 密碼（各台共用；只存在記憶體）")
        pw_row.addWidget(self.pw_edit)
        cv.addLayout(pw_row)
        lv.addWidget(cred_box)

        btn_row = QHBoxLayout()
        self.preview_btn = QPushButton("預覽計畫")
        self.preview_btn.clicked.connect(self._preview)
        self.run_btn = QPushButton("開始部署")
        self.run_btn.clicked.connect(self._start)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel)
        btn_row.addWidget(self.preview_btn)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        lv.addLayout(btn_row)

        splitter.addWidget(left)

        # 右側：terminal + 狀態表
        right = QSplitter(Qt.Orientation.Vertical)
        self.terminal = TerminalWidget()
        right.addWidget(self.terminal)
        self.status_table = QTableWidget(0, 3)
        self.status_table.setHorizontalHeaderLabels(["主機", "項目", "狀態"])
        self.status_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.status_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right.addWidget(self.status_table)
        right.setStretchFactor(0, 3)
        right.setStretchFactor(1, 1)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    # ── 案場切換 ─────────────────────────────────────────
    def set_site(self, site: Site) -> None:
        self.site = site
        self.host_list.clear()
        for h in site.hosts:
            li = QListWidgetItem(h.display)
            li.setData(Qt.ItemDataRole.UserRole, h.name)
            if h.readonly:
                li.setFlags(Qt.ItemFlag.NoItemFlags)  # 唯讀主機不可勾選
                li.setToolTip("唯讀主機：只能看，禁止部署")
            else:
                li.setFlags(li.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                li.setCheckState(Qt.CheckState.Unchecked)
            self.host_list.addItem(li)

    # ── 選取狀態 ─────────────────────────────────────────
    def _checked_hosts(self) -> list[Host]:
        assert self.site is not None
        names = []
        for i in range(self.host_list.count()):
            li = self.host_list.item(i)
            if li.checkState() == Qt.CheckState.Checked:
                names.append(li.data(Qt.ItemDataRole.UserRole))
        return [h for h in self.site.hosts if h.name in names]

    def _checked_items(self) -> list[str]:
        keys = []
        for i in range(self.sw_list.count()):
            li = self.sw_list.item(i)
            if li.checkState() == Qt.CheckState.Checked:
                keys.append(li.data(Qt.ItemDataRole.UserRole))
        return keys

    def _pick_key(self):
        path, _ = QFileDialog.getOpenFileName(self, "選擇 SSH 私鑰", str(Path.home() / ".ssh"))
        if path:
            self.key_edit.setText(path)

    # ── 參數收集（例如 NAS 掛載密碼）─────────────────────
    def _collect_params(self, item_keys: list[str]) -> dict[str, str] | None:
        assert self.site is not None
        params: dict[str, str] = {}
        for key in item_keys:
            item = self.catalog.item(key)
            for p in item.required_params:
                if self.site.env.get(p) or p in params:
                    continue
                value, ok = QInputDialog.getText(
                    self, f"{item.label} 需要參數",
                    f"請輸入 {p}：", QLineEdit.EchoMode.Password,
                )
                if not ok or not value:
                    return None
                params[p] = value
        return params

    # ── 預覽 ────────────────────────────────────────────
    def _preview(self):
        hosts, keys = self._checked_hosts(), self._checked_items()
        if not self._validate(hosts, keys):
            return
        params = self._collect_params(keys)
        if params is None:
            return
        self.terminal.append_separator("部署計畫預覽（未執行）")
        for key in keys:
            try:
                plans = self.catalog.build_plans(self.site, key, hosts, params)
            except (ValueError, PermissionError) as e:
                self.terminal.append_line("", f"✗ {self.catalog.item(key).label}: {e}")
                continue
            for plan in plans:
                self.terminal.append_line(plan.host.name, f"◆ {self.catalog.item(key).label}")
                for step in plan.steps:
                    if isinstance(step, UploadStep):
                        self.terminal.append_line(plan.host.name, f"  上傳 → {step.remote_path}")
                    elif isinstance(step, PayloadStep):
                        self.terminal.append_line(
                            plan.host.name, f"  執行 payloads/{step.payload} {step.display_args()}"
                        )

    # ── 執行 ────────────────────────────────────────────
    def _validate(self, hosts: list[Host], keys: list[str]) -> bool:
        if self.site is None:
            QMessageBox.warning(self, "提示", "尚未載入案場")
            return False
        if not hosts:
            QMessageBox.warning(self, "提示", "請勾選至少一台主機")
            return False
        if not keys:
            QMessageBox.warning(self, "提示", "請勾選至少一個軟體項目")
            return False
        return True

    def _start(self):
        hosts, keys = self._checked_hosts(), self._checked_items()
        if not self._validate(hosts, keys):
            return
        params = self._collect_params(keys)
        if params is None:
            return

        # 展開所有計畫（先驗證，全部合法才開跑）
        all_batches: list[tuple[str, list]] = []
        for key in keys:
            try:
                plans = self.catalog.build_plans(self.site, key, hosts, params)
            except (ValueError, PermissionError) as e:
                QMessageBox.critical(self, "計畫錯誤", f"{self.catalog.item(key).label}：{e}")
                return
            if plans:
                all_batches.append((key, plans))
        if not all_batches:
            QMessageBox.information(self, "提示", "勾選的軟體對所選主機都不適用")
            return

        summary = "\n".join(
            f"・{self.catalog.item(k).label} → {', '.join(p.host.name for p in plans)}"
            for k, plans in all_batches
        )
        if QMessageBox.question(
            self, "確認部署", f"將執行：\n{summary}\n\n確定開始？"
        ) != QMessageBox.StandardButton.Yes:
            return

        key_path = Path(self.key_edit.text()) if self.key_edit.text().strip() else None
        password = self.pw_edit.text() or None
        site = self.site

        def job(worker: Worker) -> bool:
            runner = PlanRunner(
                self.catalog,
                on_line=worker.emit_line,
                on_step=lambda r: worker.emit_step(r.host, r.description, r.ok),
                stop_check=lambda: worker.cancelled,
            )
            sessions: dict[str, SSHSession] = {}
            failed_hosts: set[str] = set()
            overall_ok = True
            try:
                for key, plans in all_batches:
                    label = self.catalog.item(key).label
                    worker.emit_line("", f"════ {label} ════")
                    for plan in plans:
                        if worker.cancelled:
                            worker.emit_line("", "⚠ 已取消")
                            return False
                        hname = plan.host.name
                        if hname in failed_hosts:
                            worker.emit_line(hname, f"↷ 跳過（先前步驟失敗）")
                            worker.emit_step(hname, label, False)
                            continue
                        try:
                            if hname not in sessions:
                                worker.emit_line(hname, "連線中…")
                                s = SSHSession(
                                    plan.host, key_path=key_path, password=password,
                                )
                                s.connect()
                                sessions[hname] = s
                            ok = runner.run_plan(sessions[hname], plan, password)
                        except Exception as e:  # noqa: BLE001
                            worker.emit_line(hname, f"✗ {e}")
                            ok = False
                        worker.emit_step(hname, label, ok)
                        if not ok:
                            failed_hosts.add(hname)
                            overall_ok = False
                return overall_ok
            finally:
                for s in sessions.values():
                    s.close()

        self._run_worker(job)

    def _run_worker(self, job):
        self.worker = Worker(job)
        self.worker.line.connect(self.terminal.append_line)
        self.worker.step.connect(self._add_status_row)
        self.worker.done.connect(self._on_done)
        self.run_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.terminal.append_separator("開始部署")
        self.worker.start()

    def _cancel(self):
        if self.worker:
            self.worker.cancel()
            self.terminal.append_line("", "⚠ 取消要求已送出，將於目前步驟後停止…")

    def _add_status_row(self, host: str, desc: str, ok: bool):
        row = self.status_table.rowCount()
        self.status_table.insertRow(row)
        self.status_table.setItem(row, 0, QTableWidgetItem(host))
        self.status_table.setItem(row, 1, QTableWidgetItem(desc))
        mark = QTableWidgetItem("✓ 成功" if ok else "✗ 失敗")
        mark.setForeground(Qt.GlobalColor.darkGreen if ok else Qt.GlobalColor.red)
        self.status_table.setItem(row, 2, mark)
        self.status_table.scrollToBottom()

    def _on_done(self, ok: bool, err: str):
        self.run_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.terminal.append_separator("✅ 全部完成" if ok else "⚠ 完成（有失敗項目）")
        self.worker = None
