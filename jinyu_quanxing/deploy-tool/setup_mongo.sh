#!/bin/bash
# MongoDB 原生安裝（照 evergreen .105 模式：mongod 直接裝在主機上，非 docker）
# 使用方式: ./setup_mongo.sh [--dry-run] [name]
#   - 預設對 hosts.conf 中第一台非 readonly 的 mongo 主機執行
#   - 版本與 bindIp 由 site.env 的 MONGO_VERSION / MONGO_BIND_IP 控制
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

MONGO_VERSION="${MONGO_VERSION:-7.0}"
MONGO_BIND_IP="${MONGO_BIND_IP:-0.0.0.0}"

echo ""
log_info "MongoDB 原生安裝規劃："
log_info "  主機   : ${MONGO_HOST}（$(ssh_dest "$MONGO_HOST") port $(ssh_port "$MONGO_HOST")）"
log_info "  版本   : mongodb-org ${MONGO_VERSION}（site.env 的 MONGO_VERSION 可改）"
log_info "  bindIp : ${MONGO_BIND_IP}"
log_warn "建議先到參考機確認現行版本（唯讀指令）: ./run.sh eg-mongo \"mongod --version\""
confirm "確認在 ${MONGO_HOST} 原生安裝 MongoDB？"

RS=$(mktemp "${TMPDIR:-/tmp}/jy_mongo.XXXXXX")
trap 'rm -f "$RS"' EXIT
cat > "$RS" << 'REMOTE_EOF'
#!/bin/bash
set -e
MONGO_VERSION="$1"; BIND_IP="$2"
echo "===== [remote] MongoDB 原生安裝: $(hostname) ====="

if command -v mongod >/dev/null 2>&1; then
    echo "mongod 已安裝: $(mongod --version | head -1)"
else
    . /etc/os-release
    CODENAME="${VERSION_CODENAME:?偵測不到 Ubuntu codename}"
    echo "Ubuntu codename: $CODENAME，加入 mongodb-org ${MONGO_VERSION} apt repo"

    sudo apt-get update
    sudo apt-get install -y gnupg curl
    curl -fsSL "https://www.mongodb.org/static/pgp/server-${MONGO_VERSION}.asc" \
        | sudo gpg --dearmor --yes -o "/usr/share/keyrings/mongodb-server-${MONGO_VERSION}.gpg"
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-${MONGO_VERSION}.gpg ] https://repo.mongodb.org/apt/ubuntu ${CODENAME}/mongodb-org/${MONGO_VERSION} multiverse" \
        | sudo tee "/etc/apt/sources.list.d/mongodb-org-${MONGO_VERSION}.list" >/dev/null
    sudo apt-get update
    sudo apt-get install -y mongodb-org
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

sudo systemctl enable mongod
sudo systemctl restart mongod
sleep 2

echo "--- 驗證 ---"
systemctl is-active mongod
if command -v mongosh >/dev/null 2>&1; then
    mongosh --quiet --eval 'db.runCommand({ping:1})' && echo "✓ mongod ping OK"
else
    echo "（mongosh 不在 PATH，略過 ping 測試）"
fi
echo "===== [remote] $(hostname) MongoDB 安裝完成 ✓ ====="
REMOTE_EOF

run_remote_script "$MONGO_HOST" "$RS" "'$MONGO_VERSION' '$MONGO_BIND_IP'"

echo ""
log_info "✅ MongoDB 建置完成。後續驗證："
log_info "  ./run.sh $MONGO_HOST \"systemctl status mongod --no-pager | head -5\""
log_info "  從 EMS 機測連線: mongosh --host $(host_field "$MONGO_HOST" 6) --eval 'db.runCommand({ping:1})'"
log_warn "注意：bindIp=${MONGO_BIND_IP} 且未啟用認證時，僅適用於封閉內網；需要認證請於現場另行設定"
