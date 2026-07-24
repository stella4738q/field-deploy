"""即時 terminal 輸出面板：等寬深色、逐行附加、環形上限、依主機著色前綴。"""

from __future__ import annotations

from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

MAX_LINES = 5000

# 依主機名穩定配色（深色底上的亮色系）
_HOST_COLORS = ["#8be9fd", "#50fa7b", "#ffb86c", "#ff79c6", "#bd93f9", "#f1fa8c"]


class TerminalWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(MAX_LINES)
        font = QFont("Menlo")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(12)
        self.setFont(font)
        self.setStyleSheet(
            "QPlainTextEdit { background-color: #1e1f29; color: #f8f8f2; border: none; }"
        )

    def _host_color(self, host: str) -> str:
        return _HOST_COLORS[hash(host) % len(_HOST_COLORS)]

    def append_line(self, host: str, text: str) -> None:
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if host:
            color = self._host_color(host)
            html = f'<span style="color:{color}">[{host}]</span> {text}'
        else:
            html = text
        self.appendHtml(html)
        self.moveCursor(QTextCursor.MoveOperation.End)

    def append_separator(self, title: str) -> None:
        self.appendHtml(f'<span style="color:#6272a4">──── {title} ────</span>')
