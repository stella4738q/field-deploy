#!/bin/bash
# NAS/Samba 建置：
#   1) nas 機：安裝 samba、建立 [storage] share、設定 smbpasswd
#   2) 其他 target 機：fstab 加 cifs 掛載（managed block）、mount -a 驗證
# 使用方式: ./setup_nas.sh [--dry-run] [server|clients|all]（預設 all）
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

MODE="${1:-all}"   # server / clients / all

NAS_HOST=$(list_writable_hosts nas | head -1)
CLIENT_HOSTS=$(list_writable_hosts | grep -v "^${NAS_HOST}$" || true)

if [ -z "$NAS_HOST" ]; then
    log_error "hosts.conf 中沒有可建置的 nas 主機（readonly 不納入）"
    log_error "請先啟用新案場 jy-nas"
    exit 1
fi

# 內網 IP：其他機器用它掛載 NAS
NAS_IP=$(host_field "$NAS_HOST" 6)

# Samba 密碼：site.env 沒填則互動詢問
if [ -z "$NAS_SMB_PASSWORD" ] && [ "$DRY_RUN" != "true" ]; then
    read -r -s -p "請輸入 Samba 使用者 ${NAS_SMB_USER} 的密碼（用於 smbpasswd 與 fstab）: " NAS_SMB_PASSWORD
    echo ""
    [ -z "$NAS_SMB_PASSWORD" ] && { log_error "密碼不可為空"; exit 1; }
fi

# ══ 1) NAS server 端 ══════════════════════════════════════
if [ "$MODE" = "server" ] || [ "$MODE" = "all" ]; then
    echo ""
    log_info "NAS server: ${NAS_HOST}（share [${NAS_SHARE_NAME}] → ${NAS_SHARE_PATH}）"
    confirm "確認在 $NAS_HOST 安裝並設定 samba？"

    SMB_SNIPPET=$(mktemp "${TMPDIR:-/tmp}/jy_smb.XXXXXX")
    RS_SERVER=$(mktemp "${TMPDIR:-/tmp}/jy_nas_server.XXXXXX")
    trap 'rm -f "$SMB_SNIPPET" "$RS_SERVER"' EXIT

    render_template "$TEMPLATE_DIR/smb-storage.conf.tmpl" "$SMB_SNIPPET" \
        "SHARE_NAME=${NAS_SHARE_NAME}" \
        "SHARE_PATH=${NAS_SHARE_PATH}" \
        "SMB_USER=${NAS_SMB_USER}"

    cat > "$RS_SERVER" << 'REMOTE_EOF'
#!/bin/bash
set -e
SHARE_PATH="$1"; SMB_USER="$2"; SMB_PASSWORD="$3"
SNIPPET="/tmp/jy_smb_snippet.conf"
BEGIN_MARK="# BEGIN jinyu-quanxing deploy-tool"
END_MARK="# END jinyu-quanxing deploy-tool"

echo "===== [remote] NAS samba 設定: $(hostname) ====="
sudo apt-get update
sudo apt-get install -y samba

sudo mkdir -p "$SHARE_PATH"
sudo chown "$SMB_USER":"$SMB_USER" "$SHARE_PATH"

# 備份 + 以 managed block 寫入 share 定義（重跑會先移除舊 block）
sudo cp /etc/samba/smb.conf "/etc/samba/smb.conf.bak.$(date +%Y%m%d%H%M%S)"
sudo awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
    $0 == b {skip=1; next}
    $0 == e {skip=0; next}
    !skip {print}
' /etc/samba/smb.conf | sudo tee /etc/samba/smb.conf.new >/dev/null
{
    echo "$BEGIN_MARK"
    cat "$SNIPPET"
    echo "$END_MARK"
} | sudo tee -a /etc/samba/smb.conf.new >/dev/null
sudo mv /etc/samba/smb.conf.new /etc/samba/smb.conf
rm -f "$SNIPPET"

testparm -s >/dev/null || { echo "✗ smb.conf 語法檢查失敗"; exit 1; }

# 設定 samba 使用者密碼
printf '%s\n%s\n' "$SMB_PASSWORD" "$SMB_PASSWORD" | sudo smbpasswd -a -s "$SMB_USER"

sudo systemctl enable --now smbd
sudo systemctl restart smbd
echo "===== [remote] NAS 設定完成 ✓ ====="
REMOTE_EOF

    log_step "上傳 share 設定片段到 $NAS_HOST ..."
    do_scp "$NAS_HOST" "$SMB_SNIPPET" "/tmp/jy_smb_snippet.conf"
    run_remote_script "$NAS_HOST" "$RS_SERVER" "'$NAS_SHARE_PATH' '$NAS_SMB_USER' '$NAS_SMB_PASSWORD'"
    log_info "✓ NAS server 設定完成"
fi

# ══ 2) client 端掛載 ══════════════════════════════════════
if [ "$MODE" = "clients" ] || [ "$MODE" = "all" ]; then
    if [ -z "${CLIENT_HOSTS// /}" ]; then
        log_warn "沒有其他 target 主機需要掛載，跳過 client 設定"
        exit 0
    fi

    echo ""
    log_info "將在以下主機掛載 //${NAS_IP}/${NAS_SHARE_NAME} → ${NAS_MOUNT_POINT}:"
    for h in $CLIENT_HOSTS; do
        log_info "  - $h"
    done
    confirm "確認設定 fstab 並掛載？"

    RS_CLIENT=$(mktemp "${TMPDIR:-/tmp}/jy_nas_client.XXXXXX")
    trap 'rm -f "$RS_CLIENT"' EXIT
    cat > "$RS_CLIENT" << 'REMOTE_EOF'
#!/bin/bash
set -e
NAS_IP="$1"; SHARE="$2"; MOUNT_POINT="$3"; SMB_USER="$4"; SMB_PASSWORD="$5"
BEGIN_MARK="# BEGIN jinyu-quanxing deploy-tool - Samba Mount"
END_MARK="# END jinyu-quanxing deploy-tool - Samba Mount"

echo "===== [remote] NAS 掛載設定: $(hostname) ====="
command -v mount.cifs >/dev/null 2>&1 || sudo apt-get install -y cifs-utils
sudo mkdir -p "$MOUNT_POINT"

# 帳密存 credentials 檔（root 600），fstab 不放明文密碼
CRED_FILE="/etc/samba/jy-nas-credentials"
sudo mkdir -p /etc/samba
printf 'username=%s\npassword=%s\n' "$SMB_USER" "$SMB_PASSWORD" | sudo tee "$CRED_FILE" >/dev/null
sudo chmod 600 "$CRED_FILE"

FSTAB_LINE="//${NAS_IP}/${SHARE} ${MOUNT_POINT} cifs credentials=${CRED_FILE},uid=1000,iocharset=utf8,_netdev 0 0"

sudo cp /etc/fstab "/etc/fstab.bak.$(date +%Y%m%d%H%M%S)"
sudo awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
    $0 == b {skip=1; next}
    $0 == e {skip=0; next}
    !skip {print}
' /etc/fstab | sudo tee /etc/fstab.new >/dev/null
{
    echo "$BEGIN_MARK"
    echo "$FSTAB_LINE"
    echo "$END_MARK"
} | sudo tee -a /etc/fstab.new >/dev/null
sudo mv /etc/fstab.new /etc/fstab

sudo systemctl daemon-reload 2>/dev/null || true
sudo mount -a
if mountpoint -q "$MOUNT_POINT"; then
    echo "✓ 掛載成功: $(df -h "$MOUNT_POINT" | tail -1)"
else
    echo "✗ 掛載失敗，請檢查 NAS 端設定與網路"
    exit 1
fi
echo "===== [remote] $(hostname) 掛載完成 ✓ ====="
REMOTE_EOF

    for h in $CLIENT_HOSTS; do
        echo ""
        log_step "──────── 掛載設定 $h ────────"
        run_remote_script "$h" "$RS_CLIENT" "'$NAS_IP' '$NAS_SHARE_NAME' '$NAS_MOUNT_POINT' '$NAS_SMB_USER' '$NAS_SMB_PASSWORD'"
        log_info "✓ $h 完成"
    done
fi

echo ""
log_info "✅ NAS/Samba 建置完成"
