#!/bin/bash

set -e

# 顏色輸出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 設定基本變數
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODBUS_READER_DIR="${SCRIPT_DIR}/../data-collection/modbus_reader"
BRANCH="evergreen-yp"
REPO_URL=""
USE_SSH=false

# 檢查 Git 認證方式
log_info "偵測 Git 認證方式..."
echo ""

if ssh -T git@gitlab.com 2>&1 | grep -q "Welcome to GitLab"; then
    REPO_URL="git@github.com:stella4738q/field-deploy.git"
    log_info "✓ 使用 SSH 認證"
    USE_SSH=true
else
    REPO_URL="https://github.com/stella4738q/field-deploy.git"
    log_warn "⚠ SSH 連線失敗，使用 HTTPS 認證"
    log_warn "  HTTPS 方式在 git pull 時需要輸入 token"
    echo ""
    log_info "建議設定 SSH 金鑰以避免每次輸入密碼："
    log_info "  1. 執行: cd ${MODBUS_READER_DIR}/scripts && ./setup_git_auth.sh"
    log_info "  2. 選擇選項 1（SSH 金鑰）"
    log_info "  3. 按照指示完成設定"
    echo ""
    read -p "是否繼續使用 HTTPS？[Y/n]: " continue_https
    if [[ $continue_https =~ ^[Nn]$ ]]; then
        log_info "請先設定 SSH 金鑰，然後重新執行此腳本"
        exit 0
    fi
    USE_SSH=false
fi
echo ""

# 檢查 Git
log_step "檢查 Git..."
if ! command -v git &> /dev/null; then
    log_error "Git 未安裝"
    exit 1
fi
log_info "✓ Git 已安裝"
echo ""

# 定義設備類別和子目錄
declare -A DEVICE_CATEGORIES
DEVICE_CATEGORIES=(
    ["bmu"]="bmu_1 bmu_2"
    ["io"]="ats mp_bess_a mp_bess_b pump water"
    ["meter"]="meter_cabinet_1 meter_cabinet_2 meter_main meter_sun_1 meter_sun_2 meter_vcb"
    ["pcs"]="pcs_1 pcs_2"
    ["relay"]="acb_mp_bess_ab vcb"
    ["tr"]="."
    ["ups"]="."
)

# 函數：克隆單一設備
clone_device() {
    local category=$1
    local device=$2
    local target_dir="${MODBUS_READER_DIR}/${category}"

    if [ "$device" != "." ]; then
        target_dir="${target_dir}/${device}"
    fi

    log_step "開始克隆: ${category}/${device}"

    # 清理舊目錄
    if [ -d "${target_dir}" ]; then
        log_warn "目錄 ${target_dir} 已存在，正在移除..."
        rm -rf "${target_dir}"
    fi

    # 建立目標目錄
    mkdir -p "${target_dir}"
    cd "${target_dir}"

    # 初始化 Git
    git init
    git remote add origin "${REPO_URL}"
    git config core.sparseCheckout true

    # 設定要克隆的檔案
    if [ "$device" = "." ]; then
        # 對於 tr 和 ups（頂層目錄）
        cat > .git/info/sparse-checkout << EOF
config/
modbus_config/
plugins/
docker-compose.yml
EOF
    else
        # 對於有子目錄的設備
        cat > .git/info/sparse-checkout << EOF
config/
modbus_config/
plugins/
docker-compose.yml
EOF
    fi

    # 拉取檔案
    log_info "拉取 ${BRANCH} 分支的檔案..."
    if git pull origin "${BRANCH}"; then
        log_info "✓ ${category}/${device} 克隆成功"
    else
        log_error "${category}/${device} 克隆失敗"
        return 1
    fi

    # 如果使用 SSH，確保 remote URL 也是 SSH 格式
    if [ "$USE_SSH" = true ]; then
        current_url=$(git remote get-url origin)
        if [[ "$current_url" != git@* ]]; then
            git remote set-url origin "${REPO_URL}"
        fi
    fi

    echo ""
}

# 主要執行流程
log_info "=========================================="
log_info "  開始克隆 modbus_reader 所有設備"
log_info "=========================================="
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
FAILED_DEVICES=()

# 遍歷所有設備類別
for category in "${!DEVICE_CATEGORIES[@]}"; do
    devices="${DEVICE_CATEGORIES[$category]}"

    log_step "處理類別: ${category}"
    echo ""

    for device in $devices; do
        if clone_device "$category" "$device"; then
            ((SUCCESS_COUNT++))
        else
            ((FAIL_COUNT++))
            FAILED_DEVICES+=("${category}/${device}")
        fi
    done
done

# 顯示結果摘要
echo ""
log_info "=========================================="
log_info "  克隆完成！"
log_info "=========================================="
log_info "成功: ${SUCCESS_COUNT} 個設備"
if [ $FAIL_COUNT -gt 0 ]; then
    log_error "失敗: ${FAIL_COUNT} 個設備"
    log_error "失敗的設備："
    for failed in "${FAILED_DEVICES[@]}"; do
        log_error "  - ${failed}"
    done
else
    log_info "✅ 所有設備克隆成功"
fi
echo ""

log_info "下一步："
log_info "1. 進入各設備目錄編輯配置檔案:"
log_info "   cd ${MODBUS_READER_DIR}/<category>/<device>"
log_info "   vim config/config.ini"
echo ""
log_info "2. 使用部署腳本啟動服務:"
log_info "   cd ${MODBUS_READER_DIR}/scripts"
log_info "   ./deploy.sh <device>"
echo ""

if [ "$USE_SSH" = true ]; then
    log_info "✅ 已使用 SSH 認證，未來 git pull 不需要輸入密碼"
else
    log_warn "⚠️  目前使用 HTTPS，每次 git pull 需要輸入 token"
    log_info "建議執行以下命令設定 SSH 認證："
    log_info "  cd ${MODBUS_READER_DIR}/scripts && ./setup_git_auth.sh"
fi
echo ""

