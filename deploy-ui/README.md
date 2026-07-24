# FEMC 案場圖形化部署工具（deploy-ui）

> 選案場 → 勾主機 × 勾軟體 → 自動部署，右側即時 terminal 顯示執行過程。
> 架構承襲 auto-modbus-reader 的 deploy_tool（PySide6 + paramiko）。
> 目標主機為案場 Ubuntu Server；**與 CLI（../deploy-tool/）共用同一份
> `payloads/` 遠端安裝腳本**，改一處兩邊生效。

## 功能

| 分頁 | 說明 |
|---|---|
| ① SSH 金鑰佈建 | 產生本機金鑰 → 密碼連線上傳公鑰 → 驗證免密碼登入；同步更新 `~/.ssh/config` alias |
| ② 環境建置 | 勾主機 × 勾軟體（基礎環境/NTP/Samba/NAS 掛載/HA/MongoDB）→ 依 SOP 順序自動部署；可先「預覽計畫」 |
| ③ 程式部署 | 選案場配置目錄（含 docker-compose.yml）→ 推送 → 逐一 `docker compose up -d` |
| ④ 儀表板 | 各主機連線 / Docker 容器 / 磁碟 / NAS 掛載 / 服務狀態一覽（只跑唯讀指令） |

案場清單直接讀 repo 的 `../sites/<案場>/hosts.conf` 與 `site.env`，
與 CLI 共用同一份設定；開新案場照 `../deploy-tool/README.md` 的說明即可。

## 安全設計

- **readonly 主機防護**：hosts.conf 標 `readonly=yes` 的主機在 UI 中不可勾選，
  catalog 層再擋一次（產生計畫即拋錯）；儀表板對其只跑唯讀指令
- 密碼**只存在記憶體**，不寫入任何設定檔
- 自管 known_hosts（使用者 config 目錄），金鑰變更即報錯（防中間人）
- sudo 密碼經 stdin 送出（`sudo -S -v` 快取憑證），不落入命令列
- 對遠端的所有變更動作執行前都有確認對話框

## 開發環境

```bash
cd deploy-ui
uv sync              # 建 .venv 並安裝 PySide6 / paramiko
uv run python main.py
```

## 測試

```bash
uv run pytest        # 純邏輯 + offscreen UI smoke test，不需真實 SSH
```

## 打包（帶去現場）

```bash
uv sync --group dev
uv run pyinstaller --noconfirm --windowed --name femc-field-deploy \
    --add-data "../deploy-tool:deploy-tool" \
    --add-data "../sites:sites" \
    main.py
# 產物在 dist/femc-field-deploy/，整個資料夾壓 zip 帶走
```

> 注意：打包會把 `deploy-tool/`（payloads、templates）與 `sites/` 一起帶入
> `_internal/`；現場要改 hosts.conf/site.env 時直接編輯
> `dist/femc-field-deploy/_internal/sites/<案場>/` 內的檔案再按「重新載入」即可，
> 不需重新打包。詳細三平台（Windows/Ubuntu/macOS）打包注意事項可參考
> auto-modbus-reader `deploy_tool/packaging/build_guide.md`。
