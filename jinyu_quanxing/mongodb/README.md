# MongoDB（原生安裝，非 docker）

照 evergreen .105 模式：**mongod 直接安裝在主機上**，不走 docker。

安裝與設定由部署工具執行：

```bash
cd ../deploy-tool
./run.sh eg-mongo "mongod --version"   # （唯讀）先到參考機確認現行版本
vim site.env                            # 設定 MONGO_VERSION / MONGO_BIND_IP
./setup_mongo.sh                        # 原生安裝到 jy-mongo
```

重點路徑（apt 版 mongodb-org 預設）：
- 設定檔：`/etc/mongod.conf`（工具改 bindIp 前會自動備份）
- 資料目錄：`/var/lib/mongodb`
- 日誌：`/var/log/mongodb/mongod.log`
- 服務：`systemctl status mongod`

注意：
- bindIp 預設開 `0.0.0.0` 供內網 EMS 機連線；未啟用認證時僅適用封閉內網，
  需要帳號認證請現場另行設定（security.authorization）
- 資料初始化/還原不在部署工具範圍，現場依需求處理
