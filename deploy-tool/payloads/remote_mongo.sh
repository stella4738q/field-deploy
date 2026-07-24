#!/bin/bash
set -e
MONGO_VERSION="$1"; BIND_IP="$2"; EMS_IPS="$3"
echo "===== [remote] MongoDB 原生安裝: $(hostname) ====="

if command -v mongod >/dev/null 2>&1; then
    echo "mongod 已安裝: $(mongod --version | head -1)"
else
    . /etc/os-release
    CODENAME="${VERSION_CODENAME:?偵測不到 Ubuntu codename}"
    echo "Ubuntu codename: $CODENAME，加入 mongodb-org ${MONGO_VERSION} apt repo"

    sudo apt-get update
    sudo apt-get install -y wget curl gnupg2 software-properties-common apt-transport-https ca-certificates
    curl -fsSL "https://www.mongodb.org/static/pgp/server-${MONGO_VERSION}.asc" \
        | sudo gpg --dearmor --yes -o "/usr/share/keyrings/mongodb-server-${MONGO_VERSION}.gpg"
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-${MONGO_VERSION}.gpg ] https://repo.mongodb.org/apt/ubuntu ${CODENAME}/mongodb-org/${MONGO_VERSION} multiverse" \
        | sudo tee "/etc/apt/sources.list.d/mongodb-org-${MONGO_VERSION}.list" >/dev/null
    sudo apt-get update

    if ! sudo apt-get install -y mongodb-org; then
        # MongoDB 5.0 在 Ubuntu 22.04+ 需要 libssl1.1（筆記中的 focal-security workaround）
        echo "⚠ 安裝失敗，嘗試 libssl1.1 workaround..."
        ARCH=$(dpkg --print-architecture)
        if [ "$ARCH" = "amd64" ]; then
            echo "deb http://security.ubuntu.com/ubuntu focal-security main" \
                | sudo tee /etc/apt/sources.list.d/focal-security.list >/dev/null
        else
            echo "deb http://ports.ubuntu.com/ubuntu-ports focal-security main restricted universe multiverse" \
                | sudo tee /etc/apt/sources.list.d/focal-security.list >/dev/null
        fi
        sudo apt-get update
        sudo apt-get install -y libssl1.1
        sudo rm /etc/apt/sources.list.d/focal-security.list
        sudo apt-get update
        sudo apt-get install -y mongodb-org
    fi
fi

# bindIp 設定（先備份）
if [ -f /etc/mongod.conf ]; then
    if grep -qE "^  bindIp: ${BIND_IP}$" /etc/mongod.conf; then
        echo "bindIp 已是 ${BIND_IP}"
    else
        sudo cp /etc/mongod.conf "/etc/mongod.conf.bak.$(date +%Y%m%d%H%M%S)"
        sudo sed -i "s/^  bindIp: .*/  bindIp: ${BIND_IP}/" /etc/mongod.conf
        echo "bindIp 已改為 ${BIND_IP}（原檔已備份）"
    fi
else
    echo "✗ 找不到 /etc/mongod.conf"; exit 1
fi

# ufw 放行（僅在 ufw 已啟用時）
if command -v ufw >/dev/null 2>&1 && sudo ufw status | grep -q "Status: active"; then
    OLD_IFS="$IFS"; IFS=','
    for ip in $EMS_IPS; do
        sudo ufw allow from "$ip" to any port 27017
        echo "ufw: 已放行 $ip → 27017"
    done
    IFS="$OLD_IFS"
else
    echo "（ufw 未啟用，跳過防火牆規則）"
fi

sudo systemctl enable mongod
sudo systemctl restart mongod
sleep 2

echo "--- 驗證 ---"
systemctl is-active mongod
if command -v mongosh >/dev/null 2>&1; then
    mongosh --quiet --eval 'db.runCommand({ping:1})' && echo "✓ mongod ping OK"
elif command -v mongo >/dev/null 2>&1; then
    mongo --quiet --eval 'db.runCommand({ping:1})' && echo "✓ mongod ping OK"
else
    echo "（mongosh/mongo 不在 PATH，略過 ping 測試）"
fi
echo "===== [remote] $(hostname) MongoDB 安裝完成 ✓ ====="
