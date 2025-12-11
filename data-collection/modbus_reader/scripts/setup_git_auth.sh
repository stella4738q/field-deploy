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

convert_remote_to_ssh() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        if git remote get-url origin 2>/dev/null | grep -q "https://"; then
            current_url=$(git remote get-url origin)
            ssh_url=$(echo "$current_url" | sed 's|https://gitlab.com/|git@gitlab.com:|')
            git remote set-url origin "$ssh_url"
            log_info "✓ Remote URL 已轉換為 SSH："
            log_info "  舊: $current_url"
            log_info "  新: $ssh_url"
        else
            log_info "✓ Remote URL 已經是 SSH 格式"
        fi
    fi
}

echo ""
log_info "=========================================="
log_info "  GitLab 認證設定助手"
log_info "=========================================="
echo ""

# 選擇認證方式
echo "請選擇認證方式："
echo "1) SSH 金鑰（推薦 - 最安全、最方便）"
echo "2) Git Credential Store（儲存 token 到檔案）"
echo "3) Git Credential Cache（暫存 token 到記憶體）"
echo ""
read -p "請選擇 [1-3]: " choice

case $choice in
    1)
        log_step "設定 SSH 金鑰認證"
        echo ""

        # 檢查是否已有 SSH 金鑰
        if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
            log_info "已找到現有的 SSH 金鑰："
            if [ -f ~/.ssh/id_ed25519.pub ]; then
                cat ~/.ssh/id_ed25519.pub
            elif [ -f ~/.ssh/id_rsa.pub ]; then
                cat ~/.ssh/id_rsa.pub
            fi
            echo ""
            read -p "是否要建立新的金鑰？[y/N]: " create_new
            if [[ ! $create_new =~ ^[Yy]$ ]]; then
                log_info "使用現有金鑰"
                echo ""

                # 測試 SSH 連線
                log_step "測試 SSH 連線..."
                if ssh -T git@gitlab.com 2>&1 | grep -q "Welcome to GitLab"; then
                    log_info "✓ SSH 連線成功！"

                    # 轉換 remote URL
                    log_step "檢查並轉換 remote URL..."
                    convert_remote_to_ssh

                    echo ""
                    log_info "=========================================="
                    log_info "  ✅ 設定完成！"
                    log_info "=========================================="
                    log_info "現在可以執行 git pull 而不需要輸入密碼"
                    echo ""
                    log_info "測試命令："
                    log_info "  git remote -v"
                    log_info "  git pull origin deploy"
                else
                    log_error "SSH 連線失敗"
                    echo ""
                    log_info "您的公鑰："
                    if [ -f ~/.ssh/id_ed25519.pub ]; then
                        cat ~/.ssh/id_ed25519.pub
                    elif [ -f ~/.ssh/id_rsa.pub ]; then
                        cat ~/.ssh/id_rsa.pub
                    fi
                    echo ""
                    log_info "請確認公鑰已添加到 GitLab："
                    log_info "1. 前往 https://gitlab.com/-/profile/keys"
                    log_info "2. 貼上公鑰並點擊 'Add key'"
                    log_info "3. 重新執行此腳本"
                fi
                exit 0
            fi
        fi

        # 建立新的 SSH 金鑰
        log_step "建立新的 SSH 金鑰..."
        read -p "請輸入您的 Email: " email

        ssh-keygen -t ed25519 -C "$email" -f ~/.ssh/id_ed25519 -N ""

        log_info "✓ SSH 金鑰已建立"
        echo ""
        log_info "您的公鑰："
        cat ~/.ssh/id_ed25519.pub
        echo ""
        log_info "下一步："
        log_info "1. 複製上面的公鑰"
        log_info "2. 前往 https://gitlab.com/-/profile/keys"
        log_info "3. 貼上公鑰並點擊 'Add key'"
        echo ""
        read -p "完成後按 Enter 繼續測試連線..."

        # 測試連線
        log_step "測試 SSH 連線..."
        if ssh -T git@gitlab.com 2>&1 | grep -q "Welcome to GitLab"; then
            log_info "✓ SSH 連線成功！"

            # 轉換 remote URL
            log_step "轉換 remote URL 為 SSH 格式..."
            convert_remote_to_ssh

            echo ""
            log_info "=========================================="
            log_info "  ✅ 全部完成！"
            log_info "=========================================="
            log_info "現在可以執行 git pull 而不需要輸入密碼"
            echo ""
            log_info "測試命令："
            log_info "  git remote -v"
            log_info "  git pull origin deploy"
        else
            log_error "SSH 連線失敗"
            log_info "請檢查公鑰是否正確添加到 GitLab"
            log_info "然後執行: ssh -T git@gitlab.com"
        fi
        ;;

    2)
        log_step "設定 Git Credential Store（永久儲存）"
        echo ""
        log_warn "⚠️  Token 會以明文儲存在 ~/.git-credentials"
        echo ""

        read -p "請輸入您的 GitLab Personal Access Token: " token

        # 啟用 credential store
        git config --global credential.helper store

        # 儲存認證
        echo "https://oauth2:${token}@gitlab.com" > ~/.git-credentials
        chmod 600 ~/.git-credentials

        log_info "✓ Credential Store 已設定"
        log_info "Token 已儲存到 ~/.git-credentials"
        log_info "下次 git pull/push 時會自動使用此 token"
        ;;

    3)
        log_step "設定 Git Credential Cache（暫存到記憶體）"
        echo ""

        read -p "請輸入快取時間（秒，預設 3600 = 1小時）: " timeout
        timeout=${timeout:-3600}

        # 啟用 credential cache
        git config --global credential.helper "cache --timeout=${timeout}"

        log_info "✓ Credential Cache 已設定"
        log_info "Token 會在記憶體中暫存 ${timeout} 秒"
        log_info "首次 git pull/push 時需要輸入 token，之後會自動使用快取"
        echo ""
        log_info "如何輸入："
        log_info "Username: oauth2"
        log_info "Password: 您的 Personal Access Token"
        ;;

    *)
        log_error "無效的選擇"
        exit 1
        ;;
esac

echo ""
log_info "=========================================="
log_info "  設定完成！"
log_info "=========================================="

