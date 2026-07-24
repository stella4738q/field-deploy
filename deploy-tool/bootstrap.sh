#!/bin/bash
# 基礎環境建置（docker + compose + 常用套件 + 時區）
# 使用方式: ./bootstrap.sh [--dry-run] <name|role|all>
#   "all" 只會包含非 readonly 的 target 主機；readonly 主機硬性拒絕
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

if [ $# -lt 1 ]; then
    echo "使用方式: $0 [--dry-run] <name|role|all>"
    exit 1
fi

SELECTOR="$1"

# 解析目標：all/role 只取非 readonly；指定單機時 readonly 直接拒絕
if [ "$SELECTOR" = "all" ]; then
    HOSTS=$(list_writable_hosts)
elif host_exists "$SELECTOR"; then
    assert_writable "$SELECTOR"
    HOSTS="$SELECTOR"
else
    HOSTS=$(list_writable_hosts "$SELECTOR")
fi

if [ -z "${HOSTS// /}" ]; then
    log_error "沒有可建置的 target 主機（readonly 主機不會被納入）"
    log_error "請先到 hosts.conf 啟用新案場 jy-* 主機"
    exit 1
fi

echo ""
log_info "將對以下主機進行環境建置（安裝 docker、compose、git、cifs-utils 等，設定時區 ${SITE_TIMEZONE}）:"
for h in $HOSTS; do
    log_info "  - ${h}（$(ssh_dest "$h") port $(ssh_port "$h")）"
done
confirm "確認執行？過程中需輸入各機的 sudo 密碼"

for h in $HOSTS; do
    echo ""
    log_step "──────── 建置 $h ────────"
    run_remote_script "$h" "$PAYLOAD_DIR/remote_bootstrap.sh" "$SITE_TIMEZONE"
    log_info "✓ $h 完成"
done

echo ""
log_info "✅ 全部完成。注意：docker 群組需重新登入才生效"
