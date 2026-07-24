# FEMC 案場部署工具（多案場 CLI）

> ## ⚠️ 最高優先安全守則
> **SSH 連上任何案場機器後，絕對不能亂動或亂改任何東西。**
> hosts.conf 中標記 `readonly=yes` 的主機（如運轉中的既有設備）**只能看**：
> 只執行唯讀指令（`cat`、`ls`、`docker ps`…），嚴禁寫檔、安裝套件、重啟服務。
> 所有寫入類腳本對 readonly 主機一律硬性拒絕，此為刻意設計，請勿繞過。

適用對象：案場 IPC 均為 **Ubuntu Server**（apt 系）。

## 多案場結構

```
field-deploy/
├── deploy-tool/              # 本工具（所有案場共用）
│   ├── lib/common.sh         # 共用函式（案場解析、readonly 防護、ssh 包裝、dry-run）
│   ├── payloads/             # 遠端安裝腳本（單一來源，CLI 與 UI 共用）
│   ├── templates/            # keepalived / haproxy / smb / ntp 模板
│   └── *.sh                  # 操作腳本（見下表）
├── deploy-ui/                # PySide6 圖形化部署工具（獨立 uv 專案）
└── sites/<案場名>/            # 每個案場一個目錄
    ├── hosts.conf            # 主機清單（name ssh_host port user role internal_ip readonly）
    ├── site.env              # 案場參數（VIP、NAS、MongoDB 版本、NTP 上游…）
    ├── ems-server-1|2/       # 渲染後的 HA 設定（setup_ha.sh 產生）
    ├── nas/  ntp/  mongodb/  # 各角色配置與說明
    └── ...
```

**案場選擇**（優先序）：腳本參數 `--site <名稱>` → 環境變數 `FD_SITE=<名稱>` →
`sites/` 只有一個案場時自動選用。

## 開新案場

```bash
cp -r sites/jinyu-quanxing sites/<新案場名>     # 以現有案場為模板
vim sites/<新案場名>/hosts.conf                 # 填主機（qx- 前綴改成新案場代號）
vim sites/<新案場名>/site.env                   # 調整 VIP、NAS、版本等參數
./run.sh --site <新案場名> --list               # 確認解析正確
```

## 現場部署 SOP

所有腳本都支援 `--dry-run`（只印出將執行的動作）；會改動遠端的腳本執行前需輸入 `yes` 確認。

### 前置作業（第一次到現場，每台都要）

新機器還沒有 SSH server 前，工具連不上去。先在**各主機 console**（接鍵盤螢幕，
或用 USB 帶 `console_prep.sh` 過去）執行：

```bash
./console_prep.sh          # 裝 openssh-server + 開機啟動，並顯示本機 IP
# 沒帶腳本的話，手動等效指令：
#   sudo apt-get update && sudo apt-get install -y openssh-server
#   sudo systemctl enable --now ssh
#   ip -4 addr        # 記下 IP 填 hosts.conf
```

### 部署流程（回到筆電）

```bash
cd deploy-tool

./run.sh --list                  # 0. 填好 hosts.conf/site.env 後確認
./setup_ssh.sh                   # 1. SSH 金鑰佈建 + ~/.ssh/config alias
./run.sh all "uname -a"          # 2. 煙霧測試
./bootstrap.sh all               # 3. 基礎環境（docker、compose、時區、openssh 常駐）
./setup_ntp.sh                   # 4. NTP container（每台；校時 + 對場內設備供時）
./setup_nas.sh                   # 5. data-collection 機 samba server + 各機 cifs 掛載
./setup_ha.sh                    # 6. EMS 雙機 HA（keepalived VIP + haproxy）
./setup_mongo.sh                 # 7. MongoDB 原生安裝（非 docker）
./deploy_app.sh <主機> <配置目錄>  # 8. 程式部署（含 docker-compose.yml 的目錄）
```

## 各腳本說明

| 腳本 | 功能 | 對 readonly 主機 |
|---|---|---|
| `console_prep.sh` | **在各主機 console 直接執行**：裝 openssh-server、顯示 IP | （不經 SSH，僅新機用） |
| `connect.sh` | 互動式 SSH 連線 | 可用，顯示警告 |
| `run.sh` | 批次執行指令（無預設指令） | 可用，逐台警告＋確認 |
| `push.sh` | rsync 推送檔案 | **拒絕** |
| `setup_ssh.sh` | 金鑰佈建＋config alias | ssh-copy-id **拒絕**（alias 仍會寫） |
| `bootstrap.sh` | docker/compose/時區/openssh/常用套件 | **拒絕** |
| `setup_ntp.sh` | NTP container 部署（chrony，每台都裝） | **拒絕** |
| `setup_nas.sh` | samba server＋cifs fstab 掛載 | **拒絕** |
| `setup_ha.sh` | keepalived＋haproxy 雙機 HA | **拒絕** |
| `setup_mongo.sh` | MongoDB 原生安裝（apt mongodb-org，非 docker） | **拒絕** |
| `deploy_app.sh` | 推配置＋docker compose up | **拒絕** |

`payloads/` 內是實際在遠端執行的安裝腳本（bootstrap / nas server / nas client /
ha / mongo / ntp / deploy app），CLI 與 deploy-ui 共用同一份，改一處兩邊生效。

## 設計細節（作法整合自 `Dropbox/FEMC/Linux Command/` 的實戰筆記）

- 改遠端設定檔（smb.conf、fstab、keepalived、haproxy、~/.ssh/config）前都會先備份 `.bak.<時間戳>`，
  且用 managed block（`# BEGIN/END jinyu-quanxing deploy-tool`）只動自己的區塊，重跑冪等
- keepalived 的網卡名稱不寫死，部署時於遠端自動偵測 default route 介面；
  兩台的 auth_pass 由 site.env 統一渲染
- haproxy 預設用發行版內建版本；要照筆記裝 PPA 2.7 → site.env 設 `HAPROXY_PPA_VERSION="2.7"`
- Samba 照筆記的 guest + force user 可寫模式（server 端不需 smbpasswd），
  並建立 samba-autostart systemd 服務確保開機啟動
- client 掛載照筆記用帳密（guest 掛載選項已不可靠），帳密存遠端
  `/etc/samba/jy-nas-credentials`（root 600），fstab 不放明文密碼
- MongoDB 原生安裝（非 docker）：預設最新穩定版 8.0（site.env 可改；保留舊版所需的
  libssl1.1 workaround）；bindIp 自動設「127.0.0.1,主機內網IP」；ufw 啟用時只放行 EMS 機 27017
- NTP：chrony container（host network + SYS_TIME），校正主機時鐘並對場內設備供時；
  部署前關閉 systemd-timesyncd
- `site.env` 的 `NAS_SMB_PASSWORD` 若填入真實密碼，**commit 前務必清空**

## 程式配置骨架（現場設備清單確定後）

femc_ems、batch_process、modbus_reader 各設備配置可從 evergreen-yp 分支複製後修改：

```bash
git archive origin/evergreen-yp evergreen_yp/ems-server-1/batch_process | tar -x
mv evergreen_yp/ems-server-1/batch_process sites/<案場>/ems-server-1/
# 逐一修改 config.ini / docker-compose.yml 中的 IP、設備位址等參數
```

Docker 映像建構與推送沿用 repo 既有 `utility/build_docker.sh`；
單機 pull-deploy 流程參考 `utility/deploy.sh`。
