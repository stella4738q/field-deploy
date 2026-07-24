# 晉瑜全興案場

四台主機（角色照既有案場模式，均為 Ubuntu Server）：

| 角色 | 說明 |
|---|---|
| ems1 / ems2 | EMS 雙機 HA（keepalived VIP + haproxy → :8888） |
| nas | Samba storage（[storage] share，guest + force user） |
| mongo | MongoDB **原生安裝**（非 docker，見 `mongodb/README.md`） |

另外**每台都部署 NTP container**（chrony：校時 + 對場內設備供時）。

尚未建置。現場確認連線資訊後：

1. `hosts.conf` 取消 `jy-*` 註解並填入實際 IP/port
2. 確認 `site.env` 參數（VIP、NAS 帳密、MongoDB 版本、NTP 上游）
3. 依 `../../deploy-tool/README.md` 的 SOP 執行

目錄內容：
- `ems-server-1|2/config_file/` — keepalived/haproxy 設定（`setup_ha.sh` 渲染產生）
- `nas/config_file/` — Samba share 片段
- `ntp/` — NTP container compose（`setup_ntp.sh` 渲染產生）
- `mongodb/` — MongoDB 原生安裝說明
