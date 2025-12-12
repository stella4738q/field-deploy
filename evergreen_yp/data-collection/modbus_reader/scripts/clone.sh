#!/bin/bash

set -e

# 顏色輸出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

# 檢查參數
if [ -z "$1" ]; then
    log_error "請提供設備名稱參數"
    echo "使用方式: ./clone.sh <EQUIPMENT>"
    echo "範例: ./clone.sh device01"
    exit 1
fi

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

EQUIPMENT="$1"
BRANCH="Stella"
TARGET_DIR="/home/femc/evergreen_yp/modbus_reader/${EQUIPMENT}"

log_info "設備名稱: ${EQUIPMENT}"
log_info "目標目錄: ${TARGET_DIR}"
# 自動偵測使用 SSH 或 HTTPS
log_info "偵測 Git 認證方式..."
echo ""

if ssh -T git@gitlab.com 2>&1 | grep -q "Welcome to GitLab"; then
    REPO_URL="git@gitlab.com:femc/rd/auto-modbus-reader.git"
    log_info "✓ 使用 SSH 認證"
    USE_SSH=true
else
    REPO_URL="https://gitlab.com/femc/rd/auto-modbus-reader.git"
    log_warn "⚠ SSH 連線失敗，使用 HTTPS 認證"
    log_warn "  HTTPS 方式在 git pull 時需要輸入 token"
    echo ""
    log_info "建議設定 SSH 金鑰以避免每次輸入密碼："
    log_info "  1. 執行: ./setup_git_auth.sh"
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

log_info "開始部分檔案克隆..."
echo ""

# 檢查 Git
log_step "檢查 Git..."
if ! command -v git &> /dev/null; then
    log_error "Git 未安裝"
    exit 1
fi
log_info "✓ Git 已安裝"
echo ""

# 清理舊目錄
if [ -d "${TARGET_DIR}" ]; then
    log_warn "目錄 ${TARGET_DIR} 已存在，正在移除..."
    rm -rf "${TARGET_DIR}"
fi

# 建立目標目錄
log_step "建立目標目錄..."
mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}"
echo ""

# 初始化 Git
log_step "初始化 Git sparse-checkout..."
git init
git remote add origin "${REPO_URL}"
git config core.sparseCheckout true

# 設定要克隆的檔案
log_info "設定要克隆的檔案："
cat > .git/info/sparse-checkout << EOF
config/
modbus_config/
plugins/
scripts/
docker-compose.yml
EOF

log_info "  - config/"
log_info "  - modbus_config/"
log_info "  - plugins/"
log_info "  - scripts/"
log_info "  - docker-compose.yml"
echo ""

# 拉取檔案
log_step "拉取 ${BRANCH} 分支的檔案..."
if git pull origin "${BRANCH}"; then
    log_info "✓ 拉取成功"
else
    log_error "拉取失敗"
    if [ "$USE_SSH" = false ]; then
        echo ""
        log_info "HTTPS 認證失敗。建議："
        log_info "1. 確認已建立 Personal Access Token"
        log_info "2. 使用 oauth2 作為 username"
        log_info "3. 使用 token 作為 password"
        echo ""
        log_info "或設定 SSH 金鑰以避免每次輸入："
        log_info "  ./setup_git_auth.sh"
    fi
    exit 1
fi
echo ""

# 如果使用 SSH，確保 remote URL 也是 SSH 格式
if [ "$USE_SSH" = true ]; then
    log_step "驗證 remote URL 設定..."
    current_url=$(git remote get-url origin)
    if [[ "$current_url" == git@* ]]; then
        log_info "✓ Remote URL 已正確設定為 SSH"
    else
        log_warn "Remote URL 不是 SSH 格式，正在修正..."
        git remote set-url origin "git@gitlab.com:femc/rd/evergreen-modbus-reader.git"
        log_info "✓ Remote URL 已更新為 SSH"
    fi
    echo ""
fi

# 顯示結果
log_info "=========================================="
log_info "  ✅ 克隆完成！"
log_info "=========================================="
log_info "目錄位置: $(pwd)"
echo ""
log_info "已克隆的檔案："
ls -lah
echo ""

log_info "下一步："
log_info "1. 編輯配置檔案:"
log_info "   vim config.ini"
echo ""
log_info "2. 啟動服務:"
log_info "   docker compose up -d"
echo ""
log_info "3. 查看狀態:"
log_info "   docker compose ps"
log_info "   docker compose logs -f"
echo ""

if [ "$USE_SSH" = true ]; then
    log_info "✅ 已使用 SSH 認證，未來 git pull 不需要輸入密碼"
else
    log_warn "⚠️  目前使用 HTTPS，每次 git pull 需要輸入 token"
    log_info "建議執行以下命令設定 SSH 認證："
    log_info "  cd scripts && ./setup_git_auth.sh"
fi
echo ""
