"""資料模型：案場與主機（對應 sites/<案場>/hosts.conf 與 site.env）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Host:
    """hosts.conf 的一列。readonly=True 的主機只能看，所有寫入操作必須拒絕。"""

    name: str
    ssh_host: str
    port: int
    user: str
    role: str  # ems / data-collection（兼 Samba storage）/ database-server
    internal_ip: str
    readonly: bool

    @property
    def display(self) -> str:
        ro = "（唯讀）" if self.readonly else ""
        return f"{self.name} — {self.user}@{self.ssh_host}:{self.port} [{self.role}]{ro}"


@dataclass
class Site:
    """一個案場：sites/<name>/ 目錄的解析結果。"""

    name: str
    path: Path
    hosts: list[Host] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    def writable_hosts(self, role: str | None = None) -> list[Host]:
        return [
            h for h in self.hosts
            if not h.readonly and (role is None or h.role == role)
        ]

    def host(self, name: str) -> Host | None:
        for h in self.hosts:
            if h.name == name:
                return h
        return None
