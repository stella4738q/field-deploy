#!/bin/bash

# 停止所有 EMS 服務的腳本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "停止 EMS 服務"
echo "=========================================="

# 1. 停止 reverse-proxy
echo ""
echo "[1/4] 停止 reverse-proxy..."
cd "$BASE_DIR/reverse_proxy"
docker compose down
echo "✓ reverse-proxy 停止完成"

# 2. 停止 web-socket-server
echo ""
echo "[2/4] 停止 web-socket-server..."
cd "$BASE_DIR/evergreen_yp_ems_web_socket_server"
docker compose down
echo "✓ web-socket-server 停止完成"

# 3. 停止 web-app
echo ""
echo "[3/4] 停止 web-app..."
cd "$BASE_DIR/evergreen_yp_ems_website"
docker compose down
echo "✓ web-app 停止完成"

# 4. 停止 web-api
echo ""
echo "[4/4] 停止 web-api..."
cd "$BASE_DIR/evergreen_yp_ems_backend_api_local"
docker compose down
echo "✓ web-api 停止完成"

echo ""
echo "✓ 所有服務已停止！"

