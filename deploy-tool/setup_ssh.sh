#!/bin/bash
# SSH 金鑰佈建 + ~/.ssh/config alias 設定
# 使用方式: ./setup_ssh.sh [--dry-run] [name ...]
#   - 不帶參數：對所有非 readonly（target）主機做 ssh-copy-id
#   - ~/.ssh/config 的 managed block 會包含全部主機的 alias（含現役機器，
#     現役機器只寫 alias 方便連線查看，不做 ssh-copy-id）
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

KEY_FILE="$HOME/.ssh/id_ed25519"
SSH_CONFIG="$HOME/.ssh/config"
BLOCK_BEGIN="# BEGIN ${SITE_NAME} deploy-tool"
BLOCK_END="# END ${SITE_NAME} deploy-tool"

# ── 1. 決定要佈建金鑰的目標主機（僅非 readonly）──
if [ $# -gt 0 ]; then
    TARGETS=""
    for n in "$@"; do
        assert_writable "$n"   # readonly 主機直接拒絕
        TARGETS="$TARGETS $n"
    done
else
    TARGETS=$(list_writable_hosts)
fi

if [ -z "${TARGETS// /}" ]; then
    log_warn "hosts.conf 中沒有可佈建的 target 主機（非 readonly）"
    log_warn "新案場主機資訊確認後，請先到 hosts.conf 取消註解 jy-* 並填入實際值"
    log_info "仍會更新 ~/.ssh/config 的連線 alias（含現役機器，僅供連線查看）"
fi

# ── 2. 產生金鑰（若無）──
log_step "檢查 SSH 金鑰..."
if [ -f "$KEY_FILE" ]; then
    log_info "✓ 已有金鑰: $KEY_FILE"
else
    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY-RUN] ssh-keygen -t ed25519 -f $KEY_FILE"
    else
        ssh-keygen -t ed25519 -f "$KEY_FILE" -N ""
        log_info "✓ 金鑰已建立: $KEY_FILE"
    fi
fi

# ── 3. 更新 ~/.ssh/config managed block（先備份、清舊塊、再追加）──
log_step "更新 ~/.ssh/config 連線 alias..."
NEW_BLOCK="$BLOCK_BEGIN"$'\n'
for h in $(list_hosts); do
    NEW_BLOCK+="Host $h"$'\n'
    NEW_BLOCK+="    HostName $(host_field "$h" 2)"$'\n'
    NEW_BLOCK+="    Port $(host_field "$h" 3)"$'\n'
    NEW_BLOCK+="    User $(host_field "$h" 4)"$'\n'
    NEW_BLOCK+="    ServerAliveInterval 30"$'\n'
    if is_readonly "$h"; then
        NEW_BLOCK+="    # ⚠ 現役機器，只能看，嚴禁改動"$'\n'
    fi
done
NEW_BLOCK+="$BLOCK_END"

if [ "$DRY_RUN" = "true" ]; then
    echo "[DRY-RUN] 將寫入 ~/.ssh/config 的 managed block:"
    echo "$NEW_BLOCK"
else
    mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"
    touch "$SSH_CONFIG"
    cp "$SSH_CONFIG" "${SSH_CONFIG}.bak.$(date +%Y%m%d%H%M%S)"
    # 移除舊的 managed block
    awk -v b="$BLOCK_BEGIN" -v e="$BLOCK_END" '
        $0 == b {skip=1; next}
        $0 == e {skip=0; next}
        !skip {print}
    ' "$SSH_CONFIG" > "${SSH_CONFIG}.tmp"
    mv "${SSH_CONFIG}.tmp" "$SSH_CONFIG"
    printf '%s\n' "$NEW_BLOCK" >> "$SSH_CONFIG"
    chmod 600 "$SSH_CONFIG"
    log_info "✓ ~/.ssh/config 已更新（舊檔已備份為 .bak.*）"
fi

# ── 4. ssh-copy-id 到 target 主機 ──
if [ -n "${TARGETS// /}" ]; then
    echo ""
    log_info "將對以下 target 主機佈建金鑰（各需輸入一次密碼）:"
    for h in $TARGETS; do
        log_info "  - $h → $(ssh_dest "$h") port $(ssh_port "$h")"
    done
    confirm "確認開始 ssh-copy-id？"

    for h in $TARGETS; do
        log_step "佈建金鑰到 $h ..."
        if [ "$DRY_RUN" = "true" ]; then
            echo "[DRY-RUN] ssh-copy-id -i ${KEY_FILE}.pub -p $(ssh_port "$h") $(ssh_dest "$h")"
        else
            ssh-copy-id -i "${KEY_FILE}.pub" -p "$(ssh_port "$h")" "$(ssh_dest "$h")"
        fi
    done

    # ── 5. 驗證免密碼登入 ──
    echo ""
    log_step "驗證免密碼登入..."
    FAIL=0
    for h in $TARGETS; do
        if [ "$DRY_RUN" = "true" ]; then
            echo "[DRY-RUN] ssh -o BatchMode=yes $h 'echo ok'"
        elif ssh -o BatchMode=yes -o ConnectTimeout=5 -p "$(ssh_port "$h")" "$(ssh_dest "$h")" "echo ok" >/dev/null 2>&1; then
            log_info "✓ $h 免密碼登入 OK"
        else
            log_error "✗ $h 免密碼登入失敗"
            FAIL=1
        fi
    done
    FIRST_TARGET=$(echo $TARGETS | awk '{print $1}')
    [ $FAIL -eq 0 ] && log_info "✅ SSH 佈建完成，之後可直接用 alias 連線，例如: ssh ${FIRST_TARGET}"
fi
