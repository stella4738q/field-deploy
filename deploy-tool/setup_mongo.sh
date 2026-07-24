#!/bin/bash
# MongoDB 原生安裝（照 evergreen .105 模式：mongod 直接裝在主機上，非 docker）
# 作法整合自過往實戰筆記（Dropbox/FEMC/Linux Command/Mongodb.txt）：
#   - mongodb-org apt repo 安裝，預設最新穩定版（site.env 的 MONGO_VERSION）
#   - 保留 libssl1.1 workaround（僅裝 5.0 等舊版失敗時才會用到）
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

MONGO_VERSION="${MONGO_VERSION:-8.0}"

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
confirm "確認在 ${MONGO_HOST} 原生安裝 MongoDB？"

run_remote_script "$MONGO_HOST" "$PAYLOAD_DIR/remote_mongo.sh" "'$MONGO_VERSION' '$MONGO_BIND_IP' '$EMS_IPS'"

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
