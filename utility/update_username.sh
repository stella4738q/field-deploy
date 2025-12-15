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

# 檢查是否有 SSH 金鑰認證
SSH_METHOD="key"
SSH_PASSWORD=""

# 測試第一台主機的 SSH 連線
log_info "檢查 SSH 連線方式..."
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "${SSH_USER}@${HOSTS[0]}" "echo 'test'" &>/dev/null; then
    log_warn "SSH 金鑰認證失敗，將使用密碼認證"

    # 檢查是否安裝 sshpass
    if ! command -v sshpass &> /dev/null; then
        log_error "未安裝 sshpass 工具"
        log_info "請執行以下命令安裝:"
        log_info "  macOS: brew install sshpass"
        log_info "  Ubuntu/Debian: sudo apt-get install sshpass"
        log_info "  CentOS/RHEL: sudo yum install sshpass"
        echo ""
        log_info "或者設定 SSH 金鑰認證:"
        log_info "  ssh-keygen -t rsa -b 4096"
        log_info "  ssh-copy-id ${SSH_USER}@<主機IP>"
        exit 1
    fi

    SSH_METHOD="password"
    read -sp "請輸入 ${SSH_USER} 的 SSH 密碼: " SSH_PASSWORD
    echo ""
else
    log_info "✓ SSH 金鑰認證可用"
fi

log_info "準備修改用戶名: ${OLD_USERNAME} -> ${NEW_USERNAME}"
echo ""

# 逐一處理每台主機
for host in "${HOSTS[@]}"; do
    log_info "正在處理主機: ${host}"

    # 根據認證方式執行命令
    if [ "${SSH_METHOD}" = "password" ]; then
        sshpass -p "${SSH_PASSWORD}" ssh -o StrictHostKeyChecking=no "${SSH_USER}@${host}" \
            "sudo usermod -l ${NEW_USERNAME} ${OLD_USERNAME} && \
             sudo groupmod -n ${NEW_USERNAME} ${OLD_USERNAME} && \
             sudo usermod -d /home/${NEW_USERNAME} -m ${NEW_USERNAME}"
    else
        ssh "${SSH_USER}@${host}" \
            "sudo usermod -l ${NEW_USERNAME} ${OLD_USERNAME} && \
             sudo groupmod -n ${NEW_USERNAME} ${OLD_USERNAME} && \
             sudo usermod -d /home/${NEW_USERNAME} -m ${NEW_USERNAME}"
    fi

    if [ $? -eq 0 ]; then
        log_info "✓ ${host} 修改成功"
    else
        log_error "✗ ${host} 修改失敗"
    fi
    echo ""
done

log_info "所有主機處理完成"
