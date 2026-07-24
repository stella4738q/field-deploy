#!/bin/bash
set -e
echo "===== [remote] NTP container 部署: $(hostname) ====="
command -v docker >/dev/null 2>&1 || { echo "✗ 尚未安裝 docker，請先執行 bootstrap.sh"; exit 1; }

# 關閉 systemd-timesyncd，避免與 chrony container 互搶時鐘
sudo timedatectl set-ntp false 2>/dev/null || true

cd ~/deploy/ntp
docker compose up -d || sudo docker compose up -d
sleep 3

docker ps --filter name=ntp --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
echo "--- chrony 同步狀態 ---"
docker exec ntp chronyc tracking 2>/dev/null | head -6 \
    || echo "（container 剛啟動，稍後可用: docker exec ntp chronyc tracking 查看）"
echo "===== [remote] $(hostname) NTP 部署完成 ✓ ====="
