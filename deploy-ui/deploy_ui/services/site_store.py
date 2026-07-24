"""案場載入：掃描 repo 的 sites/ 目錄，解析 hosts.conf 與 site.env。

解析規則與 deploy-tool/lib/common.sh 一致：
- hosts.conf：# 開頭與空行忽略，空白分隔 7 欄
  name ssh_host port user role internal_ip readonly
- site.env：KEY="value" 形式（bash 可 source），行尾 # 註解忽略
"""

from __future__ import annotations

import re
from pathlib import Path

from deploy_ui.models import Host, Site

_ENV_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$')


def find_repo_root(start: Path | None = None) -> Path:
    """從 deploy-ui 往上找含 sites/ 與 deploy-tool/ 的 repo 根目錄。"""
    cur = (start or Path(__file__)).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "sites").is_dir() and (parent / "deploy-tool").is_dir():
            return parent
    raise FileNotFoundError("找不到 field-deploy repo 根目錄（需含 sites/ 與 deploy-tool/）")


def parse_hosts_conf(path: Path) -> list[Host]:
    hosts: list[Host] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split()
        if len(cols) < 7:
            continue  # 欄位不足的列直接略過（與 awk 行為一致從寬）
        hosts.append(
            Host(
                name=cols[0],
                ssh_host=cols[1],
                port=int(cols[2]),
                user=cols[3],
                role=cols[4],
                internal_ip=cols[5],
                readonly=(cols[6] == "yes"),
            )
        )
    return hosts


def parse_site_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _ENV_RE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith('"'):
            # 取第一組引號內容（引號後的 # 註解自然被丟棄）
            end = value.find('"', 1)
            value = value[1:end] if end > 0 else value[1:]
        else:
            value = value.split("#", 1)[0].strip()
        env[key] = value
    return env


def load_site(site_dir: Path) -> Site:
    return Site(
        name=site_dir.name,
        path=site_dir,
        hosts=parse_hosts_conf(site_dir / "hosts.conf"),
        env=parse_site_env(site_dir / "site.env"),
    )


def list_sites(repo_root: Path | None = None) -> list[Site]:
    root = repo_root or find_repo_root()
    sites: list[Site] = []
    for d in sorted((root / "sites").iterdir()):
        if d.is_dir() and (d / "hosts.conf").is_file():
            sites.append(load_site(d))
    return sites
