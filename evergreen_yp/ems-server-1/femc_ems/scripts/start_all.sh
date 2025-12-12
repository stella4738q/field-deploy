#!/bin/bash
# 启动 FEMC EMS 服务（智能模式）

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 脚本在 scripts/ 目录，返回上一级到 femc_ems 目录
cd "$SCRIPT_DIR/.."
SCRIPT_DIR="$(pwd)"

# 记录启动的服务
STARTED_SERVICES=()
FAILED_SERVICES=()

# 检查并创建网络
print_header "1. 检查 Docker 网络"
if ! docker network ls | grep -q "femc_ems_network"; then
    print_message "创建 femc_ems_network 网络..."
    docker network create femc_ems_network
    print_message "✅ 网络创建成功"
else
    print_message "✅ 网络已存在"
fi

# 启动后端 API（可选）
print_header "2. 启动后端 API (可选)"
if [ -f "$SCRIPT_DIR/evergreen_yp_ems_backend_api_local/docker-compose.yml" ]; then
    cd "$SCRIPT_DIR/evergreen_yp_ems_backend_api_local"
    if docker-compose up -d 2>/dev/null; then
        print_message "✅ 后端 API 启动成功"
        STARTED_SERVICES+=("web-api")
    else
        print_warning "⚠️  后端 API 启动失败或已跳过"
        FAILED_SERVICES+=("web-api")
    fi
else
    print_warning "⚠️  后端 API 配置文件不存在，跳过"
fi

# 启动 WebSocket 服务器（可选）
print_header "3. 启动 WebSocket 服务器 (可选)"
if [ -f "$SCRIPT_DIR/evergreen_yp_ems_web_socket_server/docker-compose.yml" ]; then
    cd "$SCRIPT_DIR/evergreen_yp_ems_web_socket_server"
    if docker-compose up -d 2>/dev/null; then
        print_message "✅ WebSocket 服务器启动成功"
        STARTED_SERVICES+=("web-socket-server")
    else
        print_warning "⚠️  WebSocket 服务器启动失败或已跳过"
        FAILED_SERVICES+=("web-socket-server")
    fi
else
    print_warning "⚠️  WebSocket 服务器配置文件不存在，跳过"
fi

# 启动前端网站（必须）
print_header "4. 启动前端网站"
if [ -f "$SCRIPT_DIR/evergreen_yp_ems_website/docker-compose.yml" ]; then
    cd "$SCRIPT_DIR/evergreen_yp_ems_website"
    if docker-compose up -d; then
        print_message "✅ 前端网站启动成功"
        STARTED_SERVICES+=("web-app")
    else
        print_error "❌ 前端网站启动失败"
        exit 1
    fi
else
    print_error "❌ 前端网站配置文件不存在"
    exit 1
fi

# 配置 nginx locations
print_header "5. 配置反向代理"
cd "$SCRIPT_DIR/reverse_proxy/configs"

# 检查每个服务并配置相应的 location
for service in "web-api" "web-socket-server" "relay-api" "tjs-3d"; do
    location_file=""
    case $service in
        "web-api") location_file="web-api.locations" ;;
        "web-socket-server") location_file="web-socket.locations" ;;
        "relay-api") location_file="relay-api.locations" ;;
        "tjs-3d") location_file="tjs-3d.locations" ;;
    esac

    # 检查服务是否在运行
    if [[ " ${STARTED_SERVICES[@]} " =~ " ${service} " ]]; then
        # 服务运行中，启用配置
        if [ -f "${location_file}.disabled" ]; then
            mv "${location_file}.disabled" "${location_file}" 2>/dev/null || true
            print_message "✓ 启用 ${service} 配置"
        elif [ -f "${location_file}" ]; then
            print_message "✓ ${service} 配置已启用"
        fi
    else
        # 服务未运行，禁用配置
        if [ -f "${location_file}" ]; then
            mv "${location_file}" "${location_file}.disabled" 2>/dev/null || true
            print_message "✗ 禁用 ${service} 配置（服务未运行）"
        fi
    fi
done

# 启动反向代理
print_header "6. 启动反向代理"
cd "$SCRIPT_DIR/reverse_proxy"
if docker-compose up -d; then
    print_message "✅ 反向代理启动成功"
else
    print_error "❌ 反向代理启动失败"
    print_error "查看日志: docker logs reverse_proxy"
    exit 1
fi

# 等待服务启动
print_message "等待服务启动..."
sleep 3

# 检查 reverse_proxy 状态
if docker ps | grep -q "reverse_proxy"; then
    print_message "✅ reverse_proxy 运行正常"
else
    print_error "❌ reverse_proxy 未运行"
    print_error "查看日志: docker logs reverse_proxy"
    exit 1
fi

# 显示运行状态
print_header "启动完成"
print_message "运行中的容器："
docker ps --filter "network=femc_ems_network" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
print_message "已启动的服务："
for service in "${STARTED_SERVICES[@]}"; do
    echo "  ✓ $service"
done

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo ""
    print_warning "未启动的服务："
    for service in "${FAILED_SERVICES[@]}"; do
        echo "  ✗ $service"
    done
fi

echo ""
print_message "访问地址："
print_message "  - 前端网站: http://localhost 或 http://127.0.0.1"
if [[ " ${STARTED_SERVICES[@]} " =~ " web-socket-server " ]]; then
    print_message "  - WebSocket: ws://localhost:8009"
fi
if [[ " ${STARTED_SERVICES[@]} " =~ " web-api " ]]; then
    print_message "  - 后端 API: http://localhost/api/"
fi

echo ""
print_message "查看日志："
for service in "${STARTED_SERVICES[@]}"; do
    echo "  docker logs $service"
done
echo "  docker logs reverse_proxy"

echo ""
print_message "测试网络: ./scripts/test_network.sh"
print_message "停止所有服务: ./scripts/stop_all.sh"

