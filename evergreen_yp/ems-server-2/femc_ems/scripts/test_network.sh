#!/bin/bash
# 测试 FEMC EMS 网络连接性

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 检查网络是否存在
print_header "1. 检查网络状态"
if docker network ls | grep -q "femc_ems_network"; then
    print_message "网络 femc_ems_network 存在"
else
    print_error "网络 femc_ems_network 不存在"
    print_info "运行: ./manage_network.sh create"
    exit 1
fi

# 列出连接到网络的容器
print_header "2. 检查运行中的容器"
CONTAINERS=$(docker ps --filter "network=femc_ems_network" --format "{{.Names}}" 2>/dev/null || echo "")

if [ -z "$CONTAINERS" ]; then
    print_error "没有容器连接到 femc_ems_network"
    print_info "运行: ./start_all.sh"
    exit 1
fi

echo "运行中的容器:"
echo "$CONTAINERS" | while read container; do
    STATUS=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
    IP=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container" 2>/dev/null || echo "N/A")
    if [ "$STATUS" = "running" ]; then
        print_message "$container ($IP)"
    else
        print_warning "$container - 状态: $STATUS"
    fi
done

# 测试容器间通信
print_header "3. 测试容器间通信"

test_connection() {
    local from_container=$1
    local to_container=$2
    local port=$3

    if docker ps --format "{{.Names}}" | grep -q "^${from_container}$" && \
       docker ps --format "{{.Names}}" | grep -q "^${to_container}$"; then

        # 尝试 ping
        if docker exec "$from_container" ping -c 1 -W 2 "$to_container" >/dev/null 2>&1; then
            print_message "$from_container → $to_container (ping)"
        else
            print_warning "$from_container → $to_container (ping 失败)"
        fi

        # 如果指定了端口，尝试连接
        if [ -n "$port" ]; then
            if docker exec "$from_container" sh -c "command -v nc >/dev/null 2>&1"; then
                if docker exec "$from_container" nc -zv "$to_container" "$port" >/dev/null 2>&1; then
                    print_message "$from_container → $to_container:$port (TCP 连接成功)"
                else
                    print_error "$from_container → $to_container:$port (TCP 连接失败)"
                fi
            fi
        fi
    else
        print_warning "跳过 $from_container → $to_container (容器未运行)"
    fi
}

# 测试 reverse_proxy 到其他服务的连接
test_connection "reverse_proxy" "web-app" "80"
test_connection "reverse_proxy" "web-api" "5000"
test_connection "reverse_proxy" "web-socket-server" "8009"

# 测试其他容器间的连接
test_connection "web-api" "web-socket-server" "8009"
test_connection "web-socket-server" "web-api" "5000"

# 测试从 Host 访问容器
print_header "4. 测试 Host → 容器"

# 测试 reverse_proxy (端口 80)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 >/dev/null 2>&1; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80)
    if [ "$HTTP_CODE" != "000" ]; then
        print_message "Host → reverse_proxy:80 (HTTP $HTTP_CODE)"
    else
        print_error "Host → reverse_proxy:80 (无响应)"
    fi
else
    print_error "Host → reverse_proxy:80 (无法连接)"
fi

# 测试 websocket (端口 8009)
if nc -zv localhost 8009 >/dev/null 2>&1; then
    print_message "Host → web-socket-server:8009 (端口开放)"
else
    print_warning "Host → web-socket-server:8009 (无法连接)"
fi

# 测试 web-api (应该无法直接访问)
if nc -zv localhost 5000 >/dev/null 2>&1; then
    print_warning "Host → web-api:5000 (端口意外开放)"
else
    print_message "Host → web-api:5000 (正确，未映射端口)"
fi

# 测试容器访问 Host
print_header "5. 测试容器 → Host"

print_info "测试容器是否可以访问 host.docker.internal"

if docker ps --format "{{.Names}}" | grep -q "^reverse_proxy$"; then
    # 测试 host.docker.internal 是否可解析
    if docker exec reverse_proxy sh -c "getent hosts host.docker.internal" >/dev/null 2>&1; then
        HOST_IP=$(docker exec reverse_proxy sh -c "getent hosts host.docker.internal | awk '{print \$1}'")
        print_message "容器可以解析 host.docker.internal → $HOST_IP"

        # 尝试 ping host
        if docker exec reverse_proxy ping -c 1 -W 2 host.docker.internal >/dev/null 2>&1; then
            print_message "容器 → Host (ping 成功)"
        else
            print_warning "容器 → Host (ping 失败，但这可能是正常的)"
        fi
    else
        print_warning "容器无法解析 host.docker.internal"
        print_info "这在某些 Docker 版本中是正常的"
    fi
else
    print_warning "reverse_proxy 容器未运行，跳过测试"
fi

# 显示网络详细信息
print_header "6. 网络详细信息"

echo "网络配置:"
docker network inspect femc_ems_network --format '{{json .IPAM.Config}}' | python3 -m json.tool 2>/dev/null || echo "无法格式化 JSON"

echo ""
echo "容器 IP 地址:"
docker network inspect femc_ems_network --format '{{range $key, $value := .Containers}}{{$value.Name}}: {{$value.IPv4Address}}{{"\n"}}{{end}}'

# 总结
print_header "测试完成"
print_info "网络互通性说明:"
echo "  ✅ 容器间通信：使用容器名称（如 web-api:5000）"
echo "  ✅ Host → 容器：通过映射的端口（如 localhost:80）"
echo "  ✅ 容器 → Host：使用 host.docker.internal 或 Host IP"
echo ""
print_info "详细说明请查看: cat QUICKSTART.md"

