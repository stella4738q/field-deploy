#!/bin/bash
# 程式部署：推送配置目錄到目標主機，遠端對每個含 docker-compose.yml 的子目錄啟動容器
# 使用方式: ./deploy_app.sh [--dry-run] <name> <配置目錄>
# 範例:     ./deploy_app.sh jy-mongo ../mongodb
#           ./deploy_app.sh jy-ems1 ../ems-server-1/batch_process
# 私有 image 需登入時，先 export DOCKER_USERNAME / DOCKER_PASSWORD（同 utility/deploy.sh 模式）
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

if [ $# -lt 2 ]; then
    echo "使用方式: $0 [--dry-run] <name> <配置目錄>"
    echo "範例:  $0 jy-mongo ../mongodb"
    exit 1
fi

NAME="$1"; SRC_DIR="$2"

assert_writable "$NAME"

if [ ! -d "$SRC_DIR" ]; then
    log_error "配置目錄不存在: $SRC_DIR"
    exit 1
fi

BASE=$(basename "$(cd "$SRC_DIR" && pwd)")
REMOTE_DIR="~/deploy/${BASE}"

COMPOSE_COUNT=$(find "$SRC_DIR" -name docker-compose.yml | wc -l | tr -d ' ')
if [ "$COMPOSE_COUNT" -eq 0 ]; then
    log_error "$SRC_DIR 底下找不到任何 docker-compose.yml"
    exit 1
fi

echo ""
log_info "即將部署到 $NAME:"
log_info "  來源: ${SRC_DIR}（含 $COMPOSE_COUNT 個 docker-compose.yml）"
log_info "  遠端: $REMOTE_DIR"
find "$SRC_DIR" -name docker-compose.yml | sed "s|^$SRC_DIR|    ・|"
confirm "確認推送並啟動容器？"

# ── 推送 ──
do_ssh "$NAME" "mkdir -p ~/deploy"
do_rsync "$NAME" "${SRC_DIR%/}/" "${REMOTE_DIR}/"

# ── 遠端啟動 ──

REMOTE_TARGET="deploy/${BASE}"
if [ "$DRY_RUN" = "true" ]; then
    echo "[DRY-RUN] 遠端將對 $REMOTE_TARGET 下所有 docker-compose.yml 執行 docker compose up -d"
else
    run_remote_script "$NAME" "$PAYLOAD_DIR/remote_deploy_app.sh" "$REMOTE_TARGET"
fi

echo ""
log_info "✅ 部署完成。查看日誌: ./run.sh $NAME \"docker logs -f <容器名>\""
