"""軟體目錄：UI 可勾選的安裝項目，對應 deploy-tool/payloads/ 的遠端腳本。

每個 SoftwareItem 把「一台主機要做什麼」展開成步驟（上傳檔案 → 跑 payload），
編排邏輯與 CLI 的 setup_*.sh 一致，payload 為同一份檔案（單一來源）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from deploy_ui.models import Host, Site


@dataclass(frozen=True)
class UploadStep:
    """上傳內容到遠端路徑（SFTP，自動建立父目錄）。"""

    remote_path: str
    content: str  # 檔案內容（模板渲染結果或原檔）
    mode: int = 0o644


@dataclass(frozen=True)
class PayloadStep:
    """上傳 payloads/<payload> 到遠端並以 bash 執行（需要 sudo 權限）。"""

    payload: str
    args: tuple[str, ...] = ()


Step = UploadStep | PayloadStep


@dataclass(frozen=True)
class HostPlan:
    host: Host
    steps: tuple[Step, ...]


def render_template(template_dir: Path, name: str, mapping: dict[str, str]) -> str:
    """與 lib/common.sh 的 render_template 等價：{{KEY}} 逐一取代。"""
    text = (template_dir / name).read_text(encoding="utf-8")
    for key, value in mapping.items():
        text = text.replace("{{" + key + "}}", value)
    return text


@dataclass(frozen=True)
class SoftwareItem:
    key: str
    label: str
    description: str
    roles: tuple[str, ...] | None = None  # None = 所有角色適用
    # 額外需要的參數（site.env 沒有時 UI 要先問），例如 NAS 掛載密碼
    required_params: tuple[str, ...] = ()

    def applicable(self, host: Host) -> bool:
        if host.readonly:
            return False
        return self.roles is None or host.role in self.roles


class Catalog:
    """依案場展開各軟體項目的執行計畫。repo_root = field-deploy 根目錄。"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.payload_dir = repo_root / "deploy-tool" / "payloads"
        self.template_dir = repo_root / "deploy-tool" / "templates"

    # ── 項目定義（順序 = 建議執行順序）──────────────────────
    ITEMS: tuple[SoftwareItem, ...] = (
        SoftwareItem(
            "bootstrap", "基礎環境",
            "Docker + compose、openssh 常駐、git/vim/cifs-utils、時區",
        ),
        SoftwareItem(
            "ntp", "NTP container",
            "chrony 容器：校正主機時鐘 + 對場內設備提供 NTP（需先裝基礎環境）",
        ),
        SoftwareItem(
            "nas_server", "Samba server",
            "NAS 機建立 [storage] share（guest + force user）+ 開機自啟",
            roles=("nas",),
        ),
        SoftwareItem(
            "nas_client", "NAS 掛載",
            "cifs 掛載 NAS share 到 /mnt/…（fstab managed block + credentials 檔）",
            roles=("ems", "mongo"),
            required_params=("NAS_SMB_PASSWORD",),
        ),
        SoftwareItem(
            "ha", "EMS 雙機 HA",
            "keepalived VIP + haproxy（需勾選 2 台 ems；第 1 台=MASTER）",
            roles=("ems",),
        ),
        SoftwareItem(
            "mongo", "MongoDB（原生）",
            "apt mongodb-org 原生安裝（非 docker）、bindIp 限內網、ufw 放行 EMS",
            roles=("mongo",),
        ),
    )

    def item(self, key: str) -> SoftwareItem:
        for it in self.ITEMS:
            if it.key == key:
                return it
        raise KeyError(key)

    # ── 展開執行計畫 ────────────────────────────────────────
    def build_plans(
        self,
        site: Site,
        item_key: str,
        hosts: list[Host],
        params: dict[str, str],
    ) -> list[HostPlan]:
        """對已勾選且 applicable 的主機展開步驟。

        params：site.env 之外/覆蓋用的參數（例如 UI 詢問到的 NAS 密碼）。
        readonly 主機在這裡再擋一次（UI 已不給勾，此為最後防線）。
        """
        env = {**site.env, **params}
        item = self.item(item_key)
        targets = [h for h in hosts if item.applicable(h)]
        for h in targets:
            if h.readonly:  # 防線：絕不對唯讀主機產生計畫
                raise PermissionError(f"{h.name} 是唯讀主機，禁止部署")

        builder = getattr(self, f"_plan_{item_key}")
        return builder(site, env, targets)

    # 各項目的步驟展開 ---------------------------------------------------
    def _plan_bootstrap(self, site: Site, env: dict, hosts: list[Host]) -> list[HostPlan]:
        tz = env.get("SITE_TIMEZONE", "Asia/Taipei")
        return [
            HostPlan(h, (PayloadStep("remote_bootstrap.sh", (tz,)),))
            for h in hosts
        ]

    def _plan_ntp(self, site: Site, env: dict, hosts: list[Host]) -> list[HostPlan]:
        compose = render_template(
            self.template_dir, "ntp-compose.yml.tmpl",
            {
                "NTP_SERVERS": env.get(
                    "NTP_SERVERS",
                    "tock.stdtime.gov.tw,watch.stdtime.gov.tw,time.google.com",
                ),
                "TZ": env.get("SITE_TIMEZONE", "Asia/Taipei"),
            },
        )
        return [
            HostPlan(h, (
                UploadStep("deploy/ntp/docker-compose.yml", compose),
                PayloadStep("remote_ntp.sh"),
            ))
            for h in hosts
        ]

    def _plan_nas_server(self, site: Site, env: dict, hosts: list[Host]) -> list[HostPlan]:
        snippet = render_template(
            self.template_dir, "smb-storage.conf.tmpl",
            {
                "SHARE_NAME": env.get("NAS_SHARE_NAME", "storage"),
                "SHARE_PATH": env.get("NAS_SHARE_PATH", "/mnt/nas/storage"),
                "SMB_USER": env.get("NAS_SMB_USER", "myuser"),
            },
        )
        return [
            HostPlan(h, (
                UploadStep("/tmp/jy_smb_snippet.conf", snippet),
                PayloadStep("remote_nas_server.sh", (
                    env.get("NAS_SHARE_PATH", "/mnt/nas/storage"),
                    env.get("NAS_SMB_USER", "myuser"),
                )),
            ))
            for h in hosts
        ]

    def _plan_nas_client(self, site: Site, env: dict, hosts: list[Host]) -> list[HostPlan]:
        nas_hosts = site.writable_hosts("nas")
        if not nas_hosts:
            raise ValueError("找不到 nas 角色主機，無法產生掛載設定")
        nas_ip = nas_hosts[0].internal_ip
        password = env.get("NAS_SMB_PASSWORD", "")
        if not password:
            raise ValueError("缺少 NAS 掛載密碼（NAS_SMB_PASSWORD）")
        args = (
            nas_ip,
            env.get("NAS_SHARE_NAME", "storage"),
            env.get("NAS_MOUNT_POINT", "/mnt/nas/storage"),
            env.get("NAS_SMB_USER", "myuser"),
            password,
        )
        return [
            HostPlan(h, (PayloadStep("remote_nas_client.sh", args),))
            for h in hosts
        ]

    def _plan_ha(self, site: Site, env: dict, hosts: list[Host]) -> list[HostPlan]:
        if len(hosts) != 2:
            raise ValueError(f"HA 需要勾選剛好 2 台 ems 主機（目前 {len(hosts)} 台）")
        vip = env.get("VIP", "192.168.100.100")
        ppa = env.get("HAPROXY_PPA_VERSION", "")
        haproxy_cfg = render_template(
            self.template_dir, "haproxy.cfg.tmpl",
            {
                "EMS1_IP": hosts[0].internal_ip,
                "EMS2_IP": hosts[1].internal_ip,
                "BACKEND_PORT": env.get("BACKEND_PORT", "8888"),
            },
        )
        check_sh = (self.template_dir / "haproxy_check.sh").read_text(encoding="utf-8")
        plans = []
        for idx, (h, state, prio) in enumerate(
            [(hosts[0], "MASTER", "101"), (hosts[1], "BACKUP", "100")], start=1
        ):
            keepalived = render_template(
                self.template_dir, "keepalived.conf.tmpl",
                {
                    "ROUTER_ID": f"keepalived_node{idx}",
                    "STATE": state,
                    "INTERFACE": "__JY_INTERFACE__",  # 遠端 payload 偵測後代入
                    "PRIORITY": prio,
                    "AUTH_PASS": env.get("KEEPALIVED_AUTH_PASS", "10149683"),
                    "VIP": vip,
                },
            )
            plans.append(HostPlan(h, (
                UploadStep("/tmp/jy_keepalived.conf", keepalived),
                UploadStep("/tmp/jy_haproxy.cfg", haproxy_cfg),
                UploadStep("/tmp/jy_haproxy_check.sh", check_sh, mode=0o755),
                PayloadStep("remote_ha.sh", (vip, ppa)),
            )))
        return plans

    def _plan_mongo(self, site: Site, env: dict, hosts: list[Host]) -> list[HostPlan]:
        plans = []
        ems_ips = ",".join(h.internal_ip for h in site.writable_hosts("ems"))
        for h in hosts:
            bind_ip = env.get("MONGO_BIND_IP") or f"127.0.0.1,{h.internal_ip}"
            plans.append(HostPlan(h, (
                PayloadStep("remote_mongo.sh", (
                    env.get("MONGO_VERSION", "8.0"),
                    bind_ip,
                    ems_ips,
                )),
            )))
        return plans
