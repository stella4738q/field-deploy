#!/bin/bash
# MongoDB 原生安裝（照 evergreen .105 模式：mongod 直接裝在主機上，非 docker）
# 作法整合自過往實戰筆記（Dropbox/FEMC/Linux Command/Mongodb.txt）：
#   - mongodb-org apt repo 安裝，含 Ubuntu 22.04+ 裝 5.0 的 libssl1.1 workaround
#   - bindIp 預設「127.0.0.1,主機內網IP」（不開 0.0.0.0）
#   - ufw 啟用時只放行 EMS 機內網 IP 連 27017
# 使用方式: ./setup_mongo.sh [--dry-run] [name]
#   - 預設對 hosts.conf 中第一台非 readonly 的 mongo 主機執行
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

if [ $# -ge 1 ]; then
    MONGO_HOST="$1"
    assert_writable "$MONGO_HOST"
else
    MONGO_HOST=$(list_writable_hosts mongo | head -1)
fi

if [ -z "$MONGO_HOST" ]; then
    log_error "hosts.conf 中沒有可建置的 mongo 主機（readonly 不納入）"
    log_error "請先啟用新案場 jy-mongo"
    exit 1
fi

MONGO_VERSION="${MONGO_VERSION:-5.0}"

# bindIp 未指定則自動用「127.0.0.1,mongo 主機內網 IP」
if [ -z "${MONGO_BIND_IP}" ]; then
    MONGO_BIND_IP="127.0.0.1,$(host_field "$MONGO_HOST" 6)"
fi

# EMS 機內網 IP（ufw 放行 27017 用），逗號分隔
EMS_IPS=""
for h in $(list_writable_hosts ems); do
    ip=$(host_field "$h" 6)
    EMS_IPS="${EMS_IPS:+${EMS_IPS},}${ip}"
done

echo ""
log_info "MongoDB 原生安裝規劃："
log_info "  主機   : ${MONGO_HOST}（$(ssh_dest "$MONGO_HOST") port $(ssh_port "$MONGO_HOST")）"
log_info "  版本   : mongodb-org ${MONGO_VERSION}（site.env 的 MONGO_VERSION 可改）"
log_info "  bindIp : ${MONGO_BIND_IP}"
log_info "  ufw    : 若已啟用，放行 27017 給 EMS 機（${EMS_IPS:-無}）"
log_warn "建議先到參考機確認現行版本（唯讀指令）: ./run.sh eg-mongo \"mongod --version\""
confirm "確認在 ${MONGO_HOST} 原生安裝 MongoDB？"

RS=$(mktemp "${TMPDIR:-/tmp}/jy_mongo.XXXXXX")
trap 'rm -f "$RS"' EXIT
cat > "$RS" << 'REMOTE_EOF'
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
REMOTE_EOF

run_remote_script "$MONGO_HOST" "$RS" "'$MONGO_VERSION' '$MONGO_BIND_IP' '$EMS_IPS'"

echo ""
log_info "✅ MongoDB 建置完成。後續驗證："
log_info "  ./run.sh $MONGO_HOST \"systemctl status mongod --no-pager | head -5\""
log_info "  從 EMS 機測連線: mongosh --host $(host_field "$MONGO_HOST" 6) --eval 'db.runCommand({ping:1})'"
echo ""
log_warn "若要啟用帳號認證（現場手動，參考 Linux Command/Mongodb.txt）："
log_warn "  1. mongosh → use admin → db.createUser({user:'root', pwd:'<密碼>',"
log_warn "     roles:['userAdminAnyDatabase','dbAdminAnyDatabase','readWriteAnyDatabase']})"
log_warn "  2. /etc/mongod.conf 加 security:\\n  authorization: enabled"
log_warn "  3. sudo systemctl restart mongod"
log_warn "備份/還原指令範例也在同一份筆記（mongodump / mongorestore）"
