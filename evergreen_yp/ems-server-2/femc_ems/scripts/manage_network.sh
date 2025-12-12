#!/bin/bash
# 创建和管理 FEMC EMS 共享网络的脚本

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

NETWORK_NAME="femc_ems_network"

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查网络是否存在
check_network() {
    if docker network ls | grep -q "$NETWORK_NAME"; then
        return 0
    else
        return 1
    fi
}

# 创建网络
create_network() {
    print_message "创建 Docker 网络: $NETWORK_NAME"
    docker network create "$NETWORK_NAME" --driver bridge
    print_message "✅ 网络创建成功"
}

# 删除网络
remove_network() {
    print_message "删除 Docker 网络: $NETWORK_NAME"
    docker network rm "$NETWORK_NAME"
    print_message "✅ 网络删除成功"
}

# 显示网络信息
show_network() {
    print_message "网络详细信息:"
    docker network inspect "$NETWORK_NAME"
}

# 列出连接到网络的容器
list_containers() {
    print_message "连接到 $NETWORK_NAME 的容器:"
    docker network inspect "$NETWORK_NAME" -f '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}'
}

# 主函数
case "${1:-}" in
    create)
        if check_network; then
            print_warning "网络 $NETWORK_NAME 已存在"
            list_containers
        else
            create_network
        fi
        ;;
    remove|delete)
        if check_network; then
            remove_network
        else
            print_warning "网络 $NETWORK_NAME 不存在"
        fi
        ;;
    info|inspect)
        if check_network; then
            show_network
        else
            print_error "网络 $NETWORK_NAME 不存在"
            exit 1
        fi
        ;;
    list|ls)
        if check_network; then
            list_containers
        else
            print_error "网络 $NETWORK_NAME 不存在"
            exit 1
        fi
        ;;
    check)
        if check_network; then
            print_message "✅ 网络 $NETWORK_NAME 存在"
            list_containers
        else
            print_warning "❌ 网络 $NETWORK_NAME 不存在"
            print_message "运行 '$0 create' 来创建网络"
            exit 1
        fi
        ;;
    *)
        echo "使用方式: $0 {create|remove|info|list|check}"
        echo ""
        echo "命令:"
        echo "  create  - 创建共享网络"
        echo "  remove  - 删除共享网络"
        echo "  info    - 显示网络详细信息"
        echo "  list    - 列出连接到网络的容器"
        echo "  check   - 检查网络是否存在"
        exit 1
        ;;
esac

