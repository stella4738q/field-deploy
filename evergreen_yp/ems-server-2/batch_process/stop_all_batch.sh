#!/bin/bash
# 停止所有 batch_process 的 docker-compose 服务
# 排除: build_code, rapid_deploy

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

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 需要排除的目录
EXCLUDE_DIRS=("build_code" "rapid_deploy")

# 获取所有包含 docker-compose.yml 的目录
SERVICES=()
for dir in */; do
    dir_name="${dir%/}"

    # 检查是否在排除列表中
    skip=false
    for exclude in "${EXCLUDE_DIRS[@]}"; do
        if [ "$dir_name" = "$exclude" ]; then
            skip=true
            break
        fi
    done

    if [ "$skip" = true ]; then
        print_warning "跳过: $dir_name"
        continue
    fi

    # 检查是否有 docker-compose.yml
    if [ -f "$dir/docker-compose.yml" ]; then
        SERVICES+=("$dir_name")
    fi
done

print_header "停止所有 Batch Process 服务"
print_message "找到 ${#SERVICES[@]} 个服务"
echo ""

# 记录停止结果
SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_SERVICES=()

# 停止每个服务（倒序停止）
for ((idx=${#SERVICES[@]}-1 ; idx>=0 ; idx--)); do
    service="${SERVICES[idx]}"
    echo ""
    print_message "停止: $service"
    cd "$SCRIPT_DIR/$service"

    if docker-compose down 2>/dev/null; then
        print_message "✅ $service 停止成功"
        ((SUCCESS_COUNT++))
    else
        print_error "❌ $service 停止失败"
        FAILED_SERVICES+=("$service")
        ((FAILED_COUNT++))
    fi
done

# 显示总结
print_header "停止完成"
echo ""
print_message "成功: $SUCCESS_COUNT"
if [ $FAILED_COUNT -gt 0 ]; then
    print_error "失败: $FAILED_COUNT"
    echo ""
    print_error "失败的服务:"
    for service in "${FAILED_SERVICES[@]}"; do
        echo "  - $service"
    done
fi

echo ""
print_message "查看剩余运行中的容器:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(NAMES|job_|essci_)" || echo "✅ 所有相关容器已停止"

echo ""
print_message "重新启动所有服务: ./start_all_batch.sh"

