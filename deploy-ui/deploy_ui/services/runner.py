"""計畫執行器：把 catalog 展開的 HostPlan 逐步跑在 SSH 連線上（無 Qt 依賴，可測）。"""

from __future__ import annotations

import shlex
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from deploy_ui.models import Host
from deploy_ui.services.catalog import Catalog, HostPlan, PayloadStep, UploadStep
from deploy_ui.services.ssh_executor import SSHSession


@dataclass
class Credentials:
    """單一主機的登入資訊（只存在記憶體）。sudo 密碼未填時沿用 SSH 密碼。"""

    key_path: Path | None = None
    password: str | None = None
    sudo_password: str | None = None

    @property
    def effective_sudo(self) -> str | None:
        return self.sudo_password or self.password


@dataclass
class StepResult:
    host: str
    description: str
    ok: bool
    detail: str = ""


class PlanRunner:
    """執行 HostPlan。on_line(host, text) 供即時 terminal；on_step(result) 供狀態表。"""

    def __init__(
        self,
        catalog: Catalog,
        *,
        on_line: Callable[[str, str], None] | None = None,
        on_step: Callable[[StepResult], None] | None = None,
    ):
        self.catalog = catalog
        self.on_line = on_line or (lambda h, t: None)
        self.on_step = on_step or (lambda r: None)

    def run_plan(self, session: SSHSession, plan: HostPlan, sudo_password: str | None) -> bool:
        """逐步驟執行；任一步失敗即中止該主機並回傳 False。"""
        host = plan.host
        for step in plan.steps:
            if isinstance(step, UploadStep):
                desc = f"上傳 {step.remote_path}"
                self.on_line(host.name, f"→ {desc}")
                try:
                    session.upload_content(step.content, step.remote_path, step.mode)
                    self._report(host, desc, True)
                except Exception as e:  # noqa: BLE001 - 逐步驟回報，不讓例外炸掉整批
                    self._report(host, desc, False, str(e))
                    return False
            elif isinstance(step, PayloadStep):
                desc = f"執行 {step.payload}"
                self.on_line(host.name, f"→ {desc} {' '.join(step.args)}")
                try:
                    ok = self._run_payload(session, step, sudo_password)
                except Exception as e:  # noqa: BLE001
                    self._report(host, desc, False, str(e))
                    return False
                self._report(host, desc, ok)
                if not ok:
                    return False
        return True

    def _run_payload(
        self, session: SSHSession, step: PayloadStep, sudo_password: str | None
    ) -> bool:
        local = self.catalog.payload_dir / step.payload
        remote = f"/tmp/fd_{step.payload}.{int(time.time())}"
        session.upload_file(local, remote, mode=0o755)
        quoted_args = " ".join(shlex.quote(a) for a in step.args)
        cmd = f"bash {shlex.quote(remote)} {quoted_args}; rc=$?; rm -f {shlex.quote(remote)}; exit $rc"
        result = session.run(
            cmd,
            on_line=lambda text: self.on_line(session.host.name, text),
            sudo_password=sudo_password,
        )
        return result.ok

    def _report(self, host: Host, desc: str, ok: bool, detail: str = "") -> None:
        mark = "✓" if ok else "✗"
        self.on_line(host.name, f"{mark} {desc}" + (f"（{detail}）" if detail else ""))
        self.on_step(StepResult(host.name, desc, ok, detail))
