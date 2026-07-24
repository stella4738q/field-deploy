# MongoDB（原生安裝，非 docker）

照 evergreen .105 模式：**mongod 直接安裝在主機上**，不走 docker。

安裝與設定由部署工具執行：

```bash
cd ../deploy-tool
vim site.env                            # 設定 MONGO_VERSION / MONGO_BIND_IP（預設最新 8.0）
./setup_mongo.sh                        # 原生安裝到 jy-mongo
```

重點路徑（apt 版 mongodb-org 預設）：
- 設定檔：`/etc/mongod.conf`（工具改 bindIp 前會自動備份）
- 資料目錄：`/var/lib/mongodb`
- 日誌：`/var/log/mongodb/mongod.log`
- 服務：`systemctl status mongod`

注意：
- bindIp 預設自動設為「127.0.0.1,主機內網IP」（照 `Linux Command/Mongodb.txt` 做法，不開 0.0.0.0）
- ufw 已啟用時，腳本會只放行 EMS 機內網 IP 連 27017
- 帳號認證（security.authorization + createUser）為現場手動步驟，
  指令參考 `Dropbox/FEMC/Linux Command/Mongodb.txt`
- 資料初始化/還原不在部署工具範圍；mongodump / mongorestore 範例同樣在該筆記
