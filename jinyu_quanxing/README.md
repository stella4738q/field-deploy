# 晉瑜全興案場部署工具

> ## ⚠️ 最高優先安全守則
> **SSH 連上任何案場機器後，絕對不能亂動或亂改任何東西。**
> hosts.conf 中 `readonly=yes` 的主機（長榮現役 IPC）**只能看**：
> 只執行唯讀指令（`cat`、`ls`、`docker ps`…），嚴禁寫檔、安裝套件、重啟服務。
> 所有寫入類腳本對 readonly 主機一律硬性拒絕，此為刻意設計，請勿繞過。

## 機器清單

### 長榮（evergreen）現役 IPC — 純參考用，唯讀
| 別名 | 連線 | 角色 |
|---|---|---|
| eg-ems1 | `ssh -p 5001 myuser@221.120.76.225` | EMS server 1（HA MASTER） |
| eg-ems2 | `ssh -p 5002 myuser@221.120.76.225` | EMS server 2（HA BACKUP） |
| eg-nas | `ssh -p 5003 myuser@221.120.76.225` | NAS / Samba storage |
| eg-mongo | `ssh -p 5005 oem@221.120.76.225` | MongoDB |

### 晉瑜全興新案場（部署目標）
尚未建置。現場確認連線資訊後，到 `deploy-tool/hosts.conf` 取消 `jy-*` 註解並填入實際值，
同時確認 `deploy-tool/site.env` 的 VIP、NAS 等參數。

## 目錄結構

```
jinyu_quanxing/
├── deploy-tool/          # 部署工具（bash 腳本集）
│   ├── hosts.conf        # 主機清單（含 readonly 標記）
│   ├── site.env          # 案場參數
│   ├── lib/common.sh     # 共用函式（readonly 防護在這）
│   ├── templates/        # keepalived / haproxy / smb 模板
│   └── *.sh              # 見下方各腳本說明
├── ems-server-1/config_file/   # EMS1 的 keepalived(MASTER)/haproxy 設定（setup_ha.sh 產生）
├── ems-server-2/config_file/   # EMS2 的 keepalived(BACKUP)/haproxy 設定
├── nas/config_file/            # Samba [storage] share 設定
└── mongodb/                    # MongoDB 原生安裝說明（非 docker，照 evergreen .105 模式）
```

## 現場部署 SOP

所有腳本都支援 `--dry-run`（只印出將執行的動作）；會改動遠端的腳本執行前需輸入 `yes` 確認。

```bash
cd jinyu_quanxing/deploy-tool

# 0. 填 hosts.conf（啟用 jy-* 主機）與 site.env，然後檢查
./run.sh --list

# 1. SSH 金鑰佈建 + ~/.ssh/config alias（各機各輸入一次密碼）
./setup_ssh.sh

# 2. 煙霧測試
./run.sh all "uname -a && df -h /"

# 3. 基礎環境（docker、compose、git、cifs-utils、時區）
./bootstrap.sh all

# 4. NAS：samba server + 各機 cifs 掛載
./setup_nas.sh

# 5. EMS 雙機 HA（keepalived VIP + haproxy）
./setup_ha.sh

# 6. MongoDB 原生安裝（非 docker；版本先參考 eg-mongo，見 mongodb/README.md）
./setup_mongo.sh

# 7. 程式部署（對含 docker-compose.yml 的目錄通用）
./deploy_app.sh jy-ems1 ../ems-server-1/batch_process   # 配置備妥後
```

日常操作：
```bash
./connect.sh eg-ems1              # 快速連線（現役機器會顯示唯讀警告）
./run.sh ems "docker ps"          # 對某角色批次執行
./push.sh jy-ems1 <本地> <遠端>    # 推檔案（readonly 主機拒絕）
```

## 各腳本說明

| 腳本 | 功能 | 對 readonly 主機 |
|---|---|---|
| `connect.sh` | 互動式 SSH 連線 | 可用，顯示警告 |
| `run.sh` | 批次執行指令（無預設指令） | 可用，逐台警告＋確認 |
| `push.sh` | rsync 推送檔案 | **拒絕** |
| `setup_ssh.sh` | 金鑰佈建＋config alias | ssh-copy-id **拒絕**（alias 仍會寫，僅供連線） |
| `bootstrap.sh` | docker/compose/時區/常用套件 | **拒絕** |
| `setup_nas.sh` | samba server＋cifs fstab 掛載 | **拒絕** |
| `setup_ha.sh` | keepalived＋haproxy 雙機 HA | **拒絕** |
| `setup_mongo.sh` | MongoDB 原生安裝（apt mongodb-org，非 docker） | **拒絕** |
| `deploy_app.sh` | 推配置＋docker compose up | **拒絕** |

設計細節（作法整合自 `Dropbox/FEMC/Linux Command/` 的實戰筆記）：
- 改遠端設定檔（smb.conf、fstab、keepalived、haproxy、~/.ssh/config）前都會先備份 `.bak.<時間戳>`，
  且用 managed block（`# BEGIN/END jinyu-quanxing deploy-tool`）只動自己的區塊，重跑冪等
- keepalived 的網卡名稱不寫死（evergreen 是 eno1），部署時於遠端自動偵測 default route 介面；
  兩台的 auth_pass 由 site.env 統一渲染（避免筆記中兩台不一致的問題）
- haproxy 預設用發行版內建版本；要照筆記裝 PPA 2.7 → site.env 設 `HAPROXY_PPA_VERSION="2.7"`
- Samba 照筆記的 guest + force user 可寫模式（server 端不需 smbpasswd），
  並建立 samba-autostart systemd 服務確保開機啟動
- client 掛載照筆記用帳密（guest 掛載選項已不可靠），帳密存遠端
  `/etc/samba/jy-nas-credentials`（root 600），fstab 不放明文密碼
- MongoDB 原生安裝（非 docker）：預設最新穩定版 8.0（site.env 可改；保留舊版所需的
  libssl1.1 workaround）；bindIp 自動設「127.0.0.1,主機內網IP」；ufw 啟用時只放行 EMS 機 27017
- `site.env` 的 `NAS_SMB_PASSWORD` 若填入真實密碼，**commit 前務必清空**

## 程式配置骨架（現場設備清單確定後）

femc_ems、batch_process、modbus_reader 各設備配置可從 evergreen-yp 分支複製後修改：

```bash
# 在 repo 內任一位置，把 evergreen 的目錄結構取出到新案場目錄
git archive origin/evergreen-yp evergreen_yp/ems-server-1/batch_process | tar -x
mv evergreen_yp/ems-server-1/batch_process jinyu_quanxing/ems-server-1/
# 然後逐一修改 config.ini / docker-compose.yml 中的 IP、設備位址等參數

# 單一檔案參考也可以直接看：
git show origin/evergreen-yp:evergreen_yp/ems-server-1/batch_process/README.md
```

Docker 映像建構與推送沿用 repo 既有 `utility/build_docker.sh`；
單機 pull-deploy 流程參考 `utility/deploy.sh`。
