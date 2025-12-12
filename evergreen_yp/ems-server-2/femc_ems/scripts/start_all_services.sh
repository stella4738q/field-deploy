#!/bin/bash

# 啟動所有 EMS 服務的腳本
# 這個腳本會依序啟動所有獨立的服務

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "啟動 EMS 服務"
echo "=========================================="

# 1. 啟動 web-api
echo ""
echo "[1/4] 啟動 web-api..."
(cd "$BASE_DIR/evergreen_yp_ems_backend_api_local" && docker compose up -d)
if [ $? -eq 0 ]; then
    echo "✓ web-api 啟動完成"
else
    echo "✗ web-api 啟動失敗"
fi

# 2. 啟動 web-app
echo ""
echo "[2/4] 啟動 web-app..."
(cd "$BASE_DIR/evergreen_yp_ems_website" && docker compose up -d)
if [ $? -eq 0 ]; then
    echo "✓ web-app 啟動完成"
else
    echo "✗ web-app 啟動失敗"
fi

# 3. 啟動 web-socket-server
echo ""
echo "[3/4] 啟動 web-socket-server..."
(cd "$BASE_DIR/evergreen_yp_ems_web_socket_server" && docker compose up -d)
if [ $? -eq 0 ]; then
    echo "✓ web-socket-server 啟動完成"
else
    echo "✗ web-socket-server 啟動失敗"
fi

# 4. 啟動 reverse-proxy
echo ""
echo "[4/4] 啟動 reverse-proxy..."
(cd "$BASE_DIR/reverse_proxy" && docker compose up -d)
if [ $? -eq 0 ]; then
    echo "✓ reverse-proxy 啟動完成"
else
    echo "✗ reverse-proxy 啟動失敗"
fi

# 顯示狀態
echo ""
echo "=========================================="
echo "服務狀態："
echo "=========================================="
docker ps --filter "name=web-api" --filter "name=web-app" --filter "name=web-socket-server" --filter "name=reverse_proxy" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✓ 所有服務啟動完成！"
echo "前端網址: http://localhost"
echo "API 網址: http://localhost/api/"
echo "WebSocket 網址: http://localhost/socket"

