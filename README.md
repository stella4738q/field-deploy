# field-deploy

FEMC 案場部署工具與各案場配置。

| 目錄 | 說明 |
|---|---|
| `deploy-tool/` | 多案場共用 CLI 部署工具（bash）— 使用說明見 [deploy-tool/README.md](deploy-tool/README.md) |
| `deploy-ui/` | 圖形化部署工具（PySide6，選主機 × 選軟體 → 自動部署 + 即時 terminal） |
| `sites/<案場>/` | 各案場的主機清單（hosts.conf）、參數（site.env）與配置檔 |
| `utility/` | Docker 建構/推送等既有工具腳本 |

> ⚠️ 連上案場機器**只能做被授權的事**；`readonly=yes` 標記的主機嚴禁任何改動。
