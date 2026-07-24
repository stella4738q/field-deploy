#!/bin/bash
# NTP container 部署（四台主機都裝）
#   - chrony container（cturra/ntp）：host network + SYS_TIME，校正主機時鐘，
#     並對場內 LAN 提供 NTP 服務（場內設備可指向任一台 IPC 的 IP）
#   - 部署前會關閉 systemd-timesyncd（timedatectl set-ntp false）避免互搶時鐘
#   - 需先跑過 bootstrap.sh（要有 docker）
# 使用方式: ./setup_ntp.sh [--dry-run] [name|role|all]（預設 all）
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

SELECTOR="${1:-all}"

if [ "$SELECTOR" = "all" ]; then
    HOSTS=$(list_writable_hosts)
elif host_exists "$SELECTOR"; then
    assert_writable "$SELECTOR"
    HOSTS="$SELECTOR"
else
    HOSTS=$(list_writable_hosts "$SELECTOR")
fi

if [ -z "${HOSTS// /}" ]; then
    log_error "沒有可部署的 target 主機（readonly 主機不會被納入）"
    log_error "請先到 hosts.conf 啟用新案場 jy-* 主機"
    exit 1
fi

NTP_SERVERS="${NTP_SERVERS:-tock.stdtime.gov.tw,watch.stdtime.gov.tw,time.google.com}"

# 渲染 compose 到 ../ntp/（repo 內留紀錄）
mkdir -p "$SITE_DIR/ntp"
render_template "$TEMPLATE_DIR/ntp-compose.yml.tmpl" "$SITE_DIR/ntp/docker-compose.yml" \
    "NTP_SERVERS=${NTP_SERVERS}" \
    "TZ=${SITE_TIMEZONE}"

echo ""
log_info "將在以下主機部署 NTP container（上游: ${NTP_SERVERS}）:"
for h in $HOSTS; do
    log_info "  - ${h}（$(ssh_dest "$h") port $(ssh_port "$h")）"
done
log_warn "會關閉各機的 systemd-timesyncd（改由 chrony container 校時）"
confirm "確認部署？"

for h in $HOSTS; do
    echo ""
    log_step "──────── NTP 部署 $h ────────"
    do_ssh "$h" "mkdir -p ~/deploy/ntp"
    do_rsync "$h" "$SITE_DIR/ntp/" "~/deploy/ntp/"
    run_remote_script "$h" "$PAYLOAD_DIR/remote_ntp.sh"
    log_info "✓ $h 完成"
done

echo ""
log_info "✅ NTP 部署完成。驗證："
log_info "  ./run.sh all \"docker exec ntp chronyc tracking | head -3\""
log_info "  ./run.sh all \"docker exec ntp chronyc sources\""
log_info "場內設備（PCS/電表等）的 NTP server 可指向任一台 IPC 的內網 IP"
