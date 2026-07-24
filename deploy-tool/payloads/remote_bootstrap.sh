#!/bin/bash
set -e
TZ_REGION="${1:-Asia/Taipei}"
echo "===== [remote] 環境建置開始: $(hostname) ====="

echo "--- [1/5] apt 套件 ---"
sudo apt-get update
sudo apt-get install -y openssh-server git vim htop curl rsync cifs-utils
sudo systemctl enable ssh   # 確保重開機後 SSH 還在

echo "--- [2/5] Docker ---"
if command -v docker >/dev/null 2>&1; then
    echo "docker 已安裝: $(docker --version)"
else
    sudo apt-get install -y docker.io
fi
if docker compose version >/dev/null 2>&1 || sudo docker compose version >/dev/null 2>&1; then
    echo "docker compose 已可用"
else
    sudo apt-get install -y docker-compose-v2 \
        || sudo apt-get install -y docker-compose-plugin \
        || sudo apt-get install -y docker-compose
fi

echo "--- [3/5] docker 群組 ---"
if id -nG "$USER" | grep -qw docker; then
    echo "$USER 已在 docker 群組"
else
    sudo usermod -aG docker "$USER"
    echo "已將 $USER 加入 docker 群組（重新登入後生效）"
fi

echo "--- [4/5] 時區 ---"
sudo timedatectl set-timezone "$TZ_REGION" || echo "⚠ 時區設定失敗，請手動確認"
timedatectl | grep "Time zone" || true

echo "--- [5/5] 服務啟用 ---"
sudo systemctl enable --now docker

echo "===== [remote] $(hostname) 建置完成 ✓ ====="
