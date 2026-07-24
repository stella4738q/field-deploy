"""site_store 解析測試：hosts.conf / site.env 規則需與 lib/common.sh 一致。"""

from pathlib import Path

import pytest

from deploy_ui.services.site_store import (
    find_repo_root,
    list_sites,
    parse_hosts_conf,
    parse_site_env,
)

HOSTS_SAMPLE = """\
# 註解行
#jy-x   1.2.3.4  22  u  ems  1.2.3.4  no

jy-ems1   192.168.100.101  22    myuser  ems    192.168.100.101  no
jy-nas    203.0.113.9      5003  myuser  nas    192.168.100.103  yes
"""

ENV_SAMPLE = """\
# 註解
SITE_NAME="demo"
VIP="192.168.100.100"            # 行尾註解
MONGO_BIND_IP=""
BACKEND_PORT=8888
"""


def test_parse_hosts_conf(tmp_path: Path):
    p = tmp_path / "hosts.conf"
    p.write_text(HOSTS_SAMPLE, encoding="utf-8")
    hosts = parse_hosts_conf(p)
    assert [h.name for h in hosts] == ["jy-ems1", "jy-nas"]
    assert hosts[0].port == 22 and not hosts[0].readonly
    assert hosts[1].port == 5003 and hosts[1].readonly
    assert hosts[1].role == "nas"


def test_parse_site_env(tmp_path: Path):
    p = tmp_path / "site.env"
    p.write_text(ENV_SAMPLE, encoding="utf-8")
    env = parse_site_env(p)
    assert env["SITE_NAME"] == "demo"
    assert env["VIP"] == "192.168.100.100"  # 行尾註解要被丟掉
    assert env["MONGO_BIND_IP"] == ""
    assert env["BACKEND_PORT"] == "8888"


def test_find_repo_root_and_list_sites():
    root = find_repo_root()
    assert (root / "deploy-tool" / "payloads").is_dir()
    sites = list_sites(root)
    names = [s.name for s in sites]
    assert "jinyu-quanxing" in names
    jy = next(s for s in sites if s.name == "jinyu-quanxing")
    assert jy.env.get("SITE_NAME") == "jinyu-quanxing"
