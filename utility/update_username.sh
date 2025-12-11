#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日誌函數
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 檢查參數
if [ $# -lt 2 ]; then
    log_error "參數不足"
    echo "使用方式: ./update_username.sh <舊用戶名> <新用戶名>"
    echo "範例: ./update_username.sh olduser newuser"
    exit 1
fi

OLD_USERNAME="$1"
NEW_USERNAME="$2"

# 遠端主機列表
HOSTS=(
    "192.168.100.101"
    "192.168.100.102"
    "192.168.100.103"
    "192.168.100.105"
)

# SSH 用戶（用於連線的帳號）
SSH_USER="femc"

log_info "準備修改用戶名: ${OLD_USERNAME} -> ${NEW_USERNAME}"
echo ""

# 逐一處理每台主機
for host in "${HOSTS[@]}"; do
    log_info "正在處理主機: ${host}"

    # 執行用戶名修改命令
    ssh "${SSH_USER}@${host}" "sudo usermod -l ${NEW_USERNAME} ${OLD_USERNAME} && \
                                sudo groupmod -n ${NEW_USERNAME} ${OLD_USERNAME} && \
                                sudo usermod -d /home/${NEW_USERNAME} -m ${NEW_USERNAME}"

    if [ $? -eq 0 ]; then
        log_info "✓ ${host} 修改成功"
    else
        log_error "✗ ${host} 修改失敗"
    fi
    echo ""
done

log_info "所有主機處理完成"
