#!/bin/bash
# field-deploy 多案場部署工具共用函式庫
# 各腳本以 source 載入：source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"
#
# 案場選擇（三擇一，優先序由高到低）：
#   1. 腳本參數 --site <名稱>
#   2. 環境變數 FD_SITE=<名稱>
#   3. sites/ 底下只有一個案場時自動選用
#
# hosts.conf 欄位：name(1) ssh_host(2) port(3) user(4) role(5) internal_ip(6) readonly(7)
# readonly=yes 的主機只能看；所有寫入類函式一律拒絕。

# ── 顏色輸出 ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_step()  { echo -e "${BLUE}[STEP]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ── 路徑與案場解析 ────────────────────────────────────────
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$TOOL_DIR/.." && pwd)"
SITES_DIR="${REPO_ROOT}/sites"
TEMPLATE_DIR="${TOOL_DIR}/templates"
PAYLOAD_DIR="${TOOL_DIR}/payloads"

# 從呼叫端參數掃 --site（source 時可見呼叫腳本的 "$@"）
SITE="${FD_SITE:-}"
_prev=""
for _a in "$@"; do
    if [ "$_prev" = "--site" ]; then
        SITE="$_a"
    fi
    _prev="$_a"
done
unset _a _prev

# 未指定時：sites/ 只有一個案場就用它
if [ -z "$SITE" ]; then
    _count=0; _only=""
    for _d in "$SITES_DIR"/*/; do
        [ -d "$_d" ] || continue
        _count=$((_count + 1)); _only="$(basename "$_d")"
    done
    if [ "$_count" -eq 1 ]; then
        SITE="$_only"
    else
        log_error "有多個（或沒有）案場，請指定：--site <名稱> 或 export FD_SITE=<名稱>"
        log_error "可用案場："
        for _d in "$SITES_DIR"/*/; do [ -d "$_d" ] && log_error "  - $(basename "$_d")"; done
        exit 1
    fi
    unset _count _only _d
fi

SITE_DIR="${SITES_DIR}/${SITE}"
HOSTS_CONF="${SITE_DIR}/hosts.conf"
SITE_ENV="${SITE_DIR}/site.env"

if [ ! -d "$SITE_DIR" ]; then
    log_error "找不到案場目錄: $SITE_DIR"
    exit 1
fi
if [ ! -f "$HOSTS_CONF" ]; then
    log_error "找不到 hosts.conf: $HOSTS_CONF"
    exit 1
fi
# shellcheck disable=SC1090
[ -f "$SITE_ENV" ] && source "$SITE_ENV"

DRY_RUN="${DRY_RUN:-false}"

# ── hosts.conf 解析 ───────────────────────────────────────
_hosts_body() {
    grep -Ev '^[[:space:]]*(#|$)' "$HOSTS_CONF"
}

host_field() {  # host_field <name> <欄位序號>
    _hosts_body | awk -v n="$1" -v c="$2" '$1 == n { print $c; found = 1 } END { exit !found }'
}

host_exists() {
    host_field "$1" 1 >/dev/null 2>&1
}

list_hosts() {  # list_hosts [role]（省略 = 全部）
    if [ -z "${1:-}" ] || [ "$1" = "all" ]; then
        _hosts_body | awk '{print $1}'
    else
        _hosts_body | awk -v r="$1" '$5 == r {print $1}'
    fi
}

list_writable_hosts() {  # list_writable_hosts [role] — 排除 readonly 主機
    local h
    for h in $(list_hosts "${1:-}"); do
        is_readonly "$h" || echo "$h"
    done
}

resolve_hosts() {  # resolve_hosts <name|role|all> → 主機名清單
    local sel="$1" by_role
    if [ "$sel" = "all" ]; then
        list_hosts
    elif host_exists "$sel"; then
        echo "$sel"
    else
        by_role=$(list_hosts "$sel")
        if [ -n "$by_role" ]; then
            echo "$by_role"
        else
            log_error "找不到主機或角色: ${sel}（可用 --list 查看）"
            return 1
        fi
    fi
}

is_readonly() {
    [ "$(host_field "$1" 7 2>/dev/null)" = "yes" ]
}

assert_writable() {  # 寫入類腳本必經之關卡，readonly 一律硬性拒絕
    local name="$1"
    if ! host_exists "$name"; then
        log_error "找不到主機: ${name}（請確認 hosts.conf）"
        exit 1
    fi
    if is_readonly "$name"; then
        echo -e "${RED}"
        echo "  ═══════════════════════════════════════════════════════"
        echo "   ✋ ${name} 是現役運轉中的機器（readonly=yes）"
        echo "   只能查看，嚴禁任何改動。此腳本拒絕對它執行。"
        echo "  ═══════════════════════════════════════════════════════"
        echo -e "${NC}"
        exit 1
    fi
}

warn_if_readonly() {
    if is_readonly "$1"; then
        echo -e "${RED}"
        echo "  ═══════════════════════════════════════════════════════"
        echo "   ⚠⚠⚠  $1 是運行中的現役機器（唯讀）  ⚠⚠⚠"
        echo "   只能查看，嚴禁修改檔案、安裝套件或重啟服務！"
        echo "  ═══════════════════════════════════════════════════════"
        echo -e "${NC}"
    fi
}

show_hosts_table() {
    printf '%-10s %-18s %-6s %-8s %-7s %-17s %s\n' NAME SSH_HOST PORT USER ROLE INTERNAL_IP READONLY
    printf '%-10s %-18s %-6s %-8s %-7s %-17s %s\n' ---- -------- ---- ---- ---- ----------- --------
    _hosts_body | awk '{printf "%-10s %-18s %-6s %-8s %-7s %-17s %s\n", $1, $2, $3, $4, $5, $6, ($7=="yes" ? "yes ⚠現役唯讀" : "no")}'
}

# ── SSH / scp / rsync 包裝 ────────────────────────────────
ssh_dest() { echo "$(host_field "$1" 4)@$(host_field "$1" 2)"; }
ssh_port() { host_field "$1" 3; }

do_ssh() {  # do_ssh <name> <cmd>
    local name="$1"; shift
    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY-RUN] ssh -p $(ssh_port "$name") $(ssh_dest "$name") -- $*"
        return 0
    fi
    ssh -p "$(ssh_port "$name")" "$(ssh_dest "$name")" "$@"
}

do_ssh_t() {  # 需要 tty（sudo 互動輸入密碼）時
    local name="$1"; shift
    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY-RUN] ssh -t -p $(ssh_port "$name") $(ssh_dest "$name") -- $*"
        return 0
    fi
    ssh -t -p "$(ssh_port "$name")" "$(ssh_dest "$name")" "$@"
}

do_scp() {  # do_scp <name> <local> <remote>
    local name="$1" src="$2" dst="$3"
    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY-RUN] scp -P $(ssh_port "$name") $src $(ssh_dest "$name"):$dst"
        return 0
    fi
    scp -P "$(ssh_port "$name")" "$src" "$(ssh_dest "$name"):$dst"
}

do_rsync() {  # do_rsync <name> <local> <remote>（寫入類，呼叫前先 assert_writable）
    local name="$1" src="$2" dst="$3"
    assert_writable "$name"
    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY-RUN] rsync -avz -e \"ssh -p $(ssh_port "$name")\" $src $(ssh_dest "$name"):$dst"
        return 0
    fi
    rsync -avz -e "ssh -p $(ssh_port "$name")" "$src" "$(ssh_dest "$name"):$dst"
}

# 上傳本地腳本到遠端 /tmp、以 tty 執行（sudo 可互動）、結束後自動刪除
run_remote_script() {  # run_remote_script <name> <local_script> [args...]
    local name="$1" script="$2"; shift 2
    assert_writable "$name"
    local rname="/tmp/jy_deploy_$(basename "$script").$$"
    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY-RUN] scp $script → $name:$rname && ssh -t $name bash $rname $*"
        return 0
    fi
    do_scp "$name" "$script" "$rname"
    do_ssh_t "$name" "bash '$rname' $*; rc=\$?; rm -f '$rname'; exit \$rc"
}

# ── 確認與 dry-run ────────────────────────────────────────
confirm() {  # confirm "<訊息>" → 必須輸入 yes 才繼續
    local ans
    if [ "$DRY_RUN" = "true" ]; then
        log_info "(dry-run 模式，跳過確認)"
        return 0
    fi
    echo ""
    read -r -p "$1 — 輸入 yes 繼續: " ans
    if [ "$ans" != "yes" ]; then
        log_warn "已取消，未做任何變更"
        exit 0
    fi
}

# 各腳本開頭呼叫 parse_dry_run "$@" 後，以 "${ARGS[@]}" 取得其餘參數
# （同時吃掉 --dry-run 與 --site <名稱>；--site 已於 source 時生效）
parse_dry_run() {
    ARGS=()
    local a skip_next=false
    for a in "$@"; do
        if [ "$skip_next" = "true" ]; then
            skip_next=false
            continue
        fi
        case "$a" in
            --dry-run) DRY_RUN=true ;;
            --site)    skip_next=true ;;
            *)         ARGS+=("$a") ;;
        esac
    done
    log_info "案場: ${SITE}"
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "── DRY-RUN 模式：只顯示將執行的動作，不實際執行 ──"
    fi
}

# 模板渲染：render_template <template> <output> KEY=VALUE ...
render_template() {
    local tmpl="$1" out="$2"; shift 2
    local content kv key val
    content=$(cat "$tmpl")
    for kv in "$@"; do
        key="${kv%%=*}"
        val="${kv#*=}"
        content="${content//\{\{${key}\}\}/${val}}"
    done
    printf '%s\n' "$content" > "$out"
}
