#!/bin/bash

# 測試所有 EMS 服務的連接狀態

echo "=========================================="
echo "測試 EMS 服務連接"
echo "=========================================="

# 檢查容器狀態
echo ""
echo "1. 檢查容器狀態..."
echo "---"
docker ps --filter "name=web-api" --filter "name=web-app" --filter "name=web-socket-server" --filter "name=reverse_proxy" --format "table {{.Names}}\t{{.Status}}"

# 檢查網路連接
echo ""
echo "2. 檢查網路連接..."
echo "---"
echo "web-api 網路:"
docker inspect web-api --format='{{range $key, $value := .NetworkSettings.Networks}}  - {{$key}}{{end}}'
echo "web-app 網路:"
docker inspect web-app --format='{{range $key, $value := .NetworkSettings.Networks}}  - {{$key}}{{end}}'
echo "web-socket-server 網路:"
docker inspect web-socket-server --format='{{range $key, $value := .NetworkSettings.Networks}}  - {{$key}}{{end}}'
echo "reverse_proxy 網路:"
docker inspect reverse_proxy --format='{{range $key, $value := .NetworkSettings.Networks}}  - {{$key}}{{end}}'

# 測試前端訪問
echo ""
echo "3. 測試前端訪問 (http://localhost/)..."
echo "---"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
if [ "$STATUS" = "200" ]; then
    echo "✓ 前端正常 (狀態碼: $STATUS)"
else
    echo "✗ 前端異常 (狀態碼: $STATUS)"
fi

# 測試 API 訪問
echo ""
echo "4. 測試 API 訪問 (http://localhost/api/v1/)..."
echo "---"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v1/ 2>/dev/null)
if [ "$STATUS" = "200" ]; then
    echo "✓ API 正常 (狀態碼: $STATUS)"
else
    echo "✗ API 異常 (狀態碼: $STATUS)"
fi

# 測試 WebSocket 端口
echo ""
echo "5. 測試 WebSocket 端口 (http://localhost:8009/)..."
echo "---"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8009/ 2>/dev/null)
if [ "$STATUS" != "000" ]; then
    echo "✓ WebSocket 服務運行中 (狀態碼: $STATUS)"
else
    echo "✗ WebSocket 服務無回應"
fi

# 檢查最近的 API 日誌
echo ""
echo "6. 最近的 API 請求日誌..."
echo "---"
docker logs --tail 5 web-api 2>&1 | grep -E "GET|POST|PUT|DELETE" || echo "無最近請求"

echo ""
echo "=========================================="
echo "測試完成"
echo "=========================================="

