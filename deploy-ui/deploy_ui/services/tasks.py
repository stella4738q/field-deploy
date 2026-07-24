"""Qt 背景工作執行緒：長時間 SSH 作業跑在 QThread，訊號送回 UI thread。"""

from __future__ import annotations

import traceback
from collections.abc import Callable

from PySide6.QtCore import QThread, Signal


class Worker(QThread):
    """通用 worker：在背景執行 fn(worker)，以訊號回報。

    fn 內用 worker.emit_line(host, text) / worker.emit_step(...) 傳即時輸出；
    fn 回傳 bool 表整體成功與否。
    """

    line = Signal(str, str)        # (host, text) → terminal
    step = Signal(str, str, bool)  # (host, 描述, 成功) → 狀態表
    data = Signal(object)          # 任意結構化結果（例如儀表板列）
    done = Signal(bool, str)       # (成功, 錯誤訊息)

    def __init__(self, fn: Callable[["Worker"], bool], parent=None):
        super().__init__(parent)
        self._fn = fn
        self.cancelled = False

    # 供 fn 在背景 thread 內呼叫（Signal.emit 跨執行緒安全，Qt 會排入 UI 事件圈）
    def emit_line(self, host: str, text: str) -> None:
        self.line.emit(host, text)

    def emit_step(self, host: str, desc: str, ok: bool) -> None:
        self.step.emit(host, desc, ok)

    def emit_data(self, payload) -> None:
        self.data.emit(payload)

    def cancel(self) -> None:
        """協作式取消：fn 應在迴圈中檢查 worker.cancelled。"""
        self.cancelled = True

    def run(self) -> None:  # QThread entry
        try:
            ok = self._fn(self)
            self.done.emit(bool(ok), "")
        except Exception as e:  # noqa: BLE001 - 背景執行緒的最後防線
            self.line.emit("", f"✗ 發生錯誤：{e}")
            self.line.emit("", traceback.format_exc(limit=5))
            self.done.emit(False, str(e))
