"""主視窗：案場選擇 + 四個分頁（環境建置 / SSH 精靈 / 程式部署 / 儀表板）。"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QToolBar,
)

from deploy_ui.services.catalog import Catalog
from deploy_ui.services.site_store import find_repo_root, list_sites
from deploy_ui.ui.dashboard_page import DashboardPage
from deploy_ui.ui.deploy_page import DeployPage
from deploy_ui.ui.setup_page import SetupPage
from deploy_ui.ui.ssh_wizard import SshWizardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FEMC 案場部署工具")
        self.resize(1280, 800)

        self.repo_root = find_repo_root()
        self.catalog = Catalog(self.repo_root)

        # 工具列：案場選擇
        toolbar = QToolBar("案場")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addWidget(QLabel(" 案場： "))
        self.site_combo = QComboBox()
        self.site_combo.setMinimumWidth(220)
        toolbar.addWidget(self.site_combo)
        reload_btn = QPushButton("重新載入")
        reload_btn.clicked.connect(self.reload_sites)
        toolbar.addWidget(reload_btn)

        # 分頁
        self.tabs = QTabWidget()
        self.ssh_page = SshWizardPage()
        self.setup_page = SetupPage(self.catalog)
        self.deploy_page = DeployPage(self.catalog)
        self.dashboard_page = DashboardPage()
        self.tabs.addTab(self.ssh_page, "① SSH 金鑰佈建")
        self.tabs.addTab(self.setup_page, "② 環境建置")
        self.tabs.addTab(self.deploy_page, "③ 程式部署")
        self.tabs.addTab(self.dashboard_page, "④ 儀表板")
        self.setCentralWidget(self.tabs)

        self.site_combo.currentIndexChanged.connect(self._site_changed)
        self.reload_sites()

    def reload_sites(self):
        self.site_combo.blockSignals(True)
        current = self.site_combo.currentText()
        self.site_combo.clear()
        try:
            self.sites = list_sites(self.repo_root)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "錯誤", f"載入案場失敗：{e}")
            self.sites = []
        for s in self.sites:
            self.site_combo.addItem(s.name)
        if current:
            idx = self.site_combo.findText(current)
            if idx >= 0:
                self.site_combo.setCurrentIndex(idx)
        self.site_combo.blockSignals(False)
        self._site_changed()

    def _site_changed(self):
        idx = self.site_combo.currentIndex()
        if idx < 0 or idx >= len(self.sites):
            return
        site = self.sites[idx]
        for page in (self.ssh_page, self.setup_page, self.deploy_page, self.dashboard_page):
            page.set_site(site)
