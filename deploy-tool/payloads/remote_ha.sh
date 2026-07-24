#!/bin/bash
set -e
VIP="$1"; HAPROXY_PPA="$2"
echo "===== [remote] HA 設定: $(hostname) ====="

# 自動偵測 default route 的網卡
IFACE=$(ip route | awk '/^default/ {print $5; exit}')
[ -z "$IFACE" ] && { echo "✗ 偵測不到 default route 網卡"; exit 1; }
echo "使用網卡: $IFACE"

sudo apt-get update
# 指定 haproxy 版本時走 PPA（照 Linux Command 筆記，如 2.7 → ppa:vbernat/haproxy-2.7）
if [ -n "$HAPROXY_PPA" ]; then
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y "ppa:vbernat/haproxy-${HAPROXY_PPA}"
    sudo apt-get update
fi
sudo apt-get install -y keepalived haproxy
haproxy -v | head -1

sed -i "s/__JY_INTERFACE__/$IFACE/" /tmp/jy_keepalived.conf

# 備份既有設定
TS=$(date +%Y%m%d%H%M%S)
[ -f /etc/keepalived/keepalived.conf ] && sudo cp /etc/keepalived/keepalived.conf "/etc/keepalived/keepalived.conf.bak.$TS"
[ -f /etc/haproxy/haproxy.cfg ] && sudo cp /etc/haproxy/haproxy.cfg "/etc/haproxy/haproxy.cfg.bak.$TS"

sudo mkdir -p /etc/keepalived /usr/local/keepalived/log
sudo mv /tmp/jy_keepalived.conf /etc/keepalived/keepalived.conf
sudo mv /tmp/jy_haproxy.cfg /etc/haproxy/haproxy.cfg
sudo mv /tmp/jy_haproxy_check.sh /usr/local/sbin/haproxy_check.sh
sudo chmod +x /usr/local/sbin/haproxy_check.sh

# 驗證 haproxy 設定
sudo haproxy -f /etc/haproxy/haproxy.cfg -c -V

sudo systemctl enable haproxy keepalived
sudo systemctl restart haproxy
sudo systemctl restart keepalived
sleep 4
echo "--- 服務狀態 ---"
systemctl is-active haproxy keepalived
echo "--- VIP 檢查 ---"
if ip addr | grep -q "$VIP"; then
    echo "✓ VIP $VIP 目前落在本機"
else
    echo "（VIP 不在本機 — BACKUP 節點屬正常）"
fi
echo "===== [remote] $(hostname) HA 設定完成 ✓ ====="
