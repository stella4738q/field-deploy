"""catalog 展開計畫的測試：步驟編排需對應 CLI setup_*.sh 的行為。"""

from pathlib import Path

import pytest

from deploy_ui.models import Host, Site
from deploy_ui.services.catalog import Catalog, PayloadStep, UploadStep
from deploy_ui.services.site_store import find_repo_root


def _mk_site() -> Site:
    def host(name, role, ip, readonly=False):
        return Host(name, ip, 22, "myuser", role, ip, readonly)

    return Site(
        name="t",
        path=Path("/tmp"),
        hosts=[
            host("ems1", "ems", "192.168.100.101"),
            host("ems2", "ems", "192.168.100.102"),
            host("nas", "data-collection", "192.168.100.103"),
            host("mongo", "database-server", "192.168.100.105"),
            host("old", "ems", "10.0.0.9", readonly=True),
        ],
        env={
            "SITE_TIMEZONE": "Asia/Taipei",
            "VIP": "192.168.100.100",
            "BACKEND_PORT": "8888",
            "KEEPALIVED_AUTH_PASS": "10149683",
            "NAS_SHARE_NAME": "storage",
            "NAS_SHARE_PATH": "/mnt/nas/storage",
            "NAS_MOUNT_POINT": "/mnt/nas/storage",
            "NAS_SMB_USER": "myuser",
            "MONGO_VERSION": "8.0",
            "MONGO_BIND_IP": "",
        },
    )


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return Catalog(find_repo_root())


def test_bootstrap_plan(catalog):
    site = _mk_site()
    plans = catalog.build_plans(site, "bootstrap", site.hosts[:2], {})
    assert len(plans) == 2
    step = plans[0].steps[0]
    assert isinstance(step, PayloadStep)
    assert step.payload == "remote_bootstrap.sh"
    assert step.args == ("Asia/Taipei",)


def test_readonly_host_rejected(catalog):
    site = _mk_site()
    ro = site.host("old")
    # applicable 已排除 readonly，勾了也不會產生計畫
    plans = catalog.build_plans(site, "bootstrap", [ro], {})
    assert plans == []


def test_ha_requires_two_ems(catalog):
    site = _mk_site()
    with pytest.raises(ValueError):
        catalog.build_plans(site, "ha", [site.host("ems1")], {})
    plans = catalog.build_plans(site, "ha", [site.host("ems1"), site.host("ems2")], {})
    assert len(plans) == 2
    master_cfg = plans[0].steps[0]
    assert isinstance(master_cfg, UploadStep)
    assert "state MASTER" in master_cfg.content
    assert "priority 101" in master_cfg.content
    backup_cfg = plans[1].steps[0]
    assert "state BACKUP" in backup_cfg.content
    # haproxy backend 用兩台內網 IP
    haproxy = plans[0].steps[1]
    assert "192.168.100.101:8888" in haproxy.content
    assert "192.168.100.102:8888" in haproxy.content


def test_nas_client_needs_password(catalog):
    site = _mk_site()
    hosts = [site.host("ems1")]
    with pytest.raises(ValueError):
        catalog.build_plans(site, "nas_client", hosts, {})
    plans = catalog.build_plans(site, "nas_client", hosts, {"NAS_SMB_PASSWORD": "pw"})
    step = plans[0].steps[0]
    assert step.args[0] == "192.168.100.103"  # nas 內網 IP
    assert step.args[-1] == "pw"
    # 密碼在顯示層必須被遮罩（實測曾洩漏到 terminal）
    assert "pw" not in step.display_args()
    assert "***" in step.display_args()


def test_ha_vrid_from_env(catalog):
    site = _mk_site()
    site.env["KEEPALIVED_VRID"] = "77"
    plans = catalog.build_plans(site, "ha", [site.host("ems1"), site.host("ems2")], {})
    assert "virtual_router_id 77" in plans[0].steps[0].content


def test_mongo_bind_ip_auto(catalog):
    site = _mk_site()
    plans = catalog.build_plans(site, "mongo", [site.host("mongo")], {})
    step = plans[0].steps[0]
    assert step.args[1] == "127.0.0.1,192.168.100.105"
    assert step.args[2] == "192.168.100.101,192.168.100.102"


def test_payload_files_exist(catalog):
    """catalog 引用的 payload 檔必須真的存在（防呆：CLI 重構後改名）。"""
    site = _mk_site()
    combos = [
        ("bootstrap", site.hosts[:1], {}),
        ("ntp", site.hosts[:1], {}),
        ("nas_server", [site.host("nas")], {}),
        ("nas_client", [site.host("ems1")], {"NAS_SMB_PASSWORD": "x"}),
        ("ha", [site.host("ems1"), site.host("ems2")], {}),
        ("mongo", [site.host("mongo")], {}),
    ]
    for key, hosts, params in combos:
        for plan in catalog.build_plans(site, key, hosts, params):
            for step in plan.steps:
                if isinstance(step, PayloadStep):
                    assert (catalog.payload_dir / step.payload).is_file(), step.payload
