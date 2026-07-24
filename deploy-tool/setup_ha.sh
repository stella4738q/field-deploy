#!/bin/bash
# EMS 雙機 HA 建置（keepalived + haproxy，照 evergreen-yp 模式）
# 使用方式: ./setup_ha.sh [--dry-run]
#   - 取 hosts.conf 中非 readonly 的前兩台 ems：第 1 台 = MASTER(101)、第 2 台 = BACKUP(100)
#   - keepalived 網卡不寫死，於遠端自動偵測 default route 介面
#   - 渲染後的設定檔會同步存到 ../ems-server-1|2/config_file/ 作為紀錄
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"

EMS_HOSTS=($(list_writable_hosts ems))
if [ "${#EMS_HOSTS[@]}" -lt 2 ]; then
    log_error "需要 2 台非 readonly 的 ems 主機，目前只有 ${#EMS_HOSTS[@]} 台"
    log_error "請先到 hosts.conf 啟用新案場 jy-ems1 / jy-ems2"
    exit 1
fi

EMS1="${EMS_HOSTS[0]}"; EMS2="${EMS_HOSTS[1]}"
EMS1_IP=$(host_field "$EMS1" 6)
EMS2_IP=$(host_field "$EMS2" 6)

echo ""
log_info "HA 建置規劃："
log_info "  MASTER : ${EMS1}（內網 $EMS1_IP，priority 101）"
log_info "  BACKUP : ${EMS2}（內網 $EMS2_IP，priority 100）"
log_info "  VIP    : $VIP"
log_info "  Backend: ${EMS1_IP}:${BACKEND_PORT} / ${EMS2_IP}:${BACKEND_PORT}"
confirm "確認在兩台 EMS 安裝並設定 keepalived + haproxy？"

# ── 渲染設定檔（介面留 __JY_INTERFACE__ 給遠端偵測後代入）──
render_one() {  # render_one <序號 1|2> <STATE> <PRIORITY>
    local idx="$1" state="$2" prio="$3"
    local outdir="$SITE_DIR/ems-server-${idx}/config_file"
    mkdir -p "$outdir"
    render_template "$TEMPLATE_DIR/keepalived.conf.tmpl" "$outdir/keepalived.conf" \
        "ROUTER_ID=keepalived_node${idx}" \
        "STATE=${state}" \
        "INTERFACE=__JY_INTERFACE__" \
        "PRIORITY=${prio}" \
        "AUTH_PASS=${KEEPALIVED_AUTH_PASS}" \
        "VIP=${VIP}"
    render_template "$TEMPLATE_DIR/haproxy.cfg.tmpl" "$outdir/haproxy.cfg" \
        "EMS1_IP=${EMS1_IP}" \
        "EMS2_IP=${EMS2_IP}" \
        "BACKEND_PORT=${BACKEND_PORT}"
    cp "$TEMPLATE_DIR/haproxy_check.sh" "$outdir/haproxy_check.sh"
}
render_one 1 MASTER 101
render_one 2 BACKUP 100
log_info "✓ 設定檔已渲染至 ems-server-1/config_file/ 與 ems-server-2/config_file/"

deploy_ha_to() {  # deploy_ha_to <name> <序號 1|2>
    local name="$1" idx="$2"
    local cfgdir="$SITE_DIR/ems-server-${idx}/config_file"
    echo ""
    log_step "──────── HA 設定 ${name}（ems-server-${idx}）────────"
    do_scp "$name" "$cfgdir/keepalived.conf"   "/tmp/jy_keepalived.conf"
    do_scp "$name" "$cfgdir/haproxy.cfg"       "/tmp/jy_haproxy.cfg"
    do_scp "$name" "$cfgdir/haproxy_check.sh"  "/tmp/jy_haproxy_check.sh"
    run_remote_script "$name" "$PAYLOAD_DIR/remote_ha.sh" "'$VIP' '${HAPROXY_PPA_VERSION:-}'"
    log_info "✓ $name 完成"
}

deploy_ha_to "$EMS1" 1
deploy_ha_to "$EMS2" 2

echo ""
log_info "✅ HA 建置完成。驗證建議："
log_info "  ./run.sh $EMS1 \"ip addr | grep $VIP\"     # VIP 應在 MASTER"
log_info "  ./run.sh ems \"systemctl is-active keepalived haproxy\""
log_info "  瀏覽器開 http://$VIP 應可看到 EMS 頁面（服務部署後）"
