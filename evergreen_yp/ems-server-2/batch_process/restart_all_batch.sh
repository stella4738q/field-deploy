#!/bin/bash
# 重启所有 batch_process 的 docker-compose 服务
# 排除: build_code, rapid_deploy

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[✓]${NC} $1"
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

print_header "重启所有 Batch Process 服务"

print_message "步骤 1/2: 停止所有服务..."
./stop_all_batch.sh

echo ""
print_message "等待 3 秒..."
sleep 3

echo ""
print_message "步骤 2/2: 启动所有服务..."
./start_all_batch.sh

print_header "重启完成"

