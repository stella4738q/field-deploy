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

# ── 遠端腳本 ──
REMOTE_SCRIPT=$(mktemp "${TMPDIR:-/tmp}/jy_bootstrap.XXXXXX")
trap 'rm -f "$REMOTE_SCRIPT"' EXIT
cat > "$REMOTE_SCRIPT" << 'REMOTE_EOF'
#!/bin/bash
set -e
TZ_REGION="${1:-Asia/Taipei}"
echo "===== [remote] 環境建置開始: $(hostname) ====="

echo "--- [1/5] apt 套件 ---"
sudo apt-get update
sudo apt-get install -y git vim htop curl rsync cifs-utils

echo "--- [2/5] Docker ---"
if command -v docker >/dev/null 2>&1; then
    echo "docker 已安裝: $(docker --version)"
else
    sudo apt-get install -y docker.io
fi
if docker compose version >/dev/null 2>&1 || sudo docker compose version >/dev/null 2>&1; then
    echo "docker compose 已可用"
else
    sudo apt-get install -y docker-compose-v2 \
        || sudo apt-get install -y docker-compose-plugin \
        || sudo apt-get install -y docker-compose
fi

echo "--- [3/5] docker 群組 ---"
if id -nG "$USER" | grep -qw docker; then
    echo "$USER 已在 docker 群組"
else
    sudo usermod -aG docker "$USER"
    echo "已將 $USER 加入 docker 群組（重新登入後生效）"
fi

echo "--- [4/5] 時區 ---"
sudo timedatectl set-timezone "$TZ_REGION" || echo "⚠ 時區設定失敗，請手動確認"
timedatectl | grep "Time zone" || true

echo "--- [5/5] 服務啟用 ---"
sudo systemctl enable --now docker

echo "===== [remote] $(hostname) 建置完成 ✓ ====="
REMOTE_EOF

for h in $HOSTS; do
    echo ""
    log_step "──────── 建置 $h ────────"
    run_remote_script "$h" "$REMOTE_SCRIPT" "$SITE_TIMEZONE"
    log_info "✓ $h 完成"
done

echo ""
log_info "✅ 全部完成。注意：docker 群組需重新登入才生效"
