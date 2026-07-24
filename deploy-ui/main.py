"""FEMC 案場圖形化部署工具進入點。

啟動：
    cd deploy-ui
    uv sync
    uv run python main.py
"""

import sys

from PySide6.QtWidgets import QApplication

from deploy_ui.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FEMC 案場部署工具")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
