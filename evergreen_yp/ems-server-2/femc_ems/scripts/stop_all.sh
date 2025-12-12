#!/bin/bash
# 停止所有 FEMC EMS 服务

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 脚本在 scripts/ 目录，返回上一级到 femc_ems 目录
cd "$SCRIPT_DIR/.."
SCRIPT_DIR="$(pwd)"

print_message "停止所有 FEMC EMS 服务..."

# 停止反向代理
print_message "停止反向代理..."
cd "$SCRIPT_DIR/reverse_proxy"
docker-compose down

# 停止前端网站
print_message "停止前端网站..."
cd "$SCRIPT_DIR/evergreen_yp_ems_website"
docker-compose down

# 停止 WebSocket 服务器
print_message "停止 WebSocket 服务器..."
cd "$SCRIPT_DIR/evergreen_yp_ems_web_socket_server"
docker-compose down

# 停止后端 API
print_message "停止后端 API..."
cd "$SCRIPT_DIR/evergreen_yp_ems_backend_api_local"
docker-compose down

print_message ""
print_message "✅ 所有服务已停止"
print_message ""

# 询问是否删除网络
read -p "是否删除共享网络 femc_ems_network? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_message "删除网络..."
    docker network rm femc_ems_network 2>/dev/null && print_message "✅ 网络已删除" || print_warning "网络不存在或已删除"
else
    print_message "保留网络 femc_ems_network"
fi

