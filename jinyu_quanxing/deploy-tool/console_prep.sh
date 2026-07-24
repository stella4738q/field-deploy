#!/bin/bash
# ⚠ 這支不是遠端部署腳本 —— 是「第一次到現場、機器還沒有 SSH server」時，
#   直接在各主機 console（接鍵盤螢幕）上執行的前置腳本。
#   可用 USB 隨身碟帶到現場，四台（ems1/ems2/nas/mongo）都要跑一次。
#
# 做的事：裝 openssh-server 並設開機啟動、顯示本機 IP 供 hosts.conf 填寫
set -e

GREEN='\033[0;32m'
NC='\033[0m'
log() { echo -e "${GREEN}[INFO]${NC} $1"; }

log "===== 前置作業: $(hostname) ====="

# 1. SSH server
if dpkg -s openssh-server >/dev/null 2>&1; then
    log "openssh-server 已安裝"
else
    log "安裝 openssh-server..."
    sudo apt-get update
    sudo apt-get install -y openssh-server
fi
sudo systemctl enable --now ssh
log "ssh 服務狀態: $(systemctl is-active ssh)"

# 2. 顯示本機網路資訊（填 hosts.conf 用）
echo ""
log "本機 IP（把它填進 deploy-tool/hosts.conf 的 jy-* 對應列）："
ip -4 addr show | awk '/inet / && $2 !~ /^127\./ {print "  " $NF " → " $2}'
echo ""
log "✅ 完成。回到筆電後執行 deploy-tool/setup_ssh.sh 佈建金鑰"
