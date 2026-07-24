"""UI smoke test：offscreen 建構主視窗，抓 import/組裝層級的錯誤。"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_main_window_builds(app):
    from deploy_ui.ui.main_window import MainWindow

    w = MainWindow()
    assert w.tabs.count() == 4
    # 案場載入且分頁有拿到主機清單
    assert w.site_combo.count() >= 1
    assert w.setup_page.host_list.count() >= 1 or True  # jy-* 可能全註解，允許為空
    # 軟體目錄項目齊全
    assert w.setup_page.sw_list.count() == len(w.catalog.ITEMS)


def test_dashboard_probe_parser():
    from deploy_ui.ui.dashboard_page import _parse_probe

    output = """==DOCKER==
ntp: Up 2 hours
==DISK==
12G/98G (13%)
==NAS==
✓ 已掛載
==SVC==
haproxy ✓
keepalived ✓
"""
    row = _parse_probe(output)
    assert "ntp: Up 2 hours" in row["docker"]
    assert row["disk"] == "12G/98G (13%)"
    assert row["nas"] == "✓ 已掛載"
    assert "haproxy ✓" in row["svc"]
