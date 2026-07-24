#!/bin/bash
# 批次執行指令：./run.sh [--dry-run] <name|role|all> "<指令>"
# 沒有任何預設指令；readonly 主機執行前需逐台確認
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

if [ "${1:-}" = "--list" ]; then
    show_hosts_table
    exit 0
fi

if [ $# -lt 2 ]; then
    echo "使用方式: $0 [--dry-run] <name|role|all> \"<指令>\""
    echo "          $0 --list        # 列出主機"
    echo ""
    echo "範例:"
    echo "  $0 all \"uname -a\""
    echo "  $0 ems \"docker ps\""
    echo "  $0 qx-data-collection \"df -h\""
    exit 1
fi

SELECTOR="$1"; shift
CMD="$*"

HOSTS=$(resolve_hosts "$SELECTOR")

for h in $HOSTS; do
    echo ""
    log_step "──────── $h ────────"
    if is_readonly "$h"; then
        warn_if_readonly "$h"
        if [ "$DRY_RUN" != "true" ]; then
            read -r -p "確定要在現役機器 $h 執行「$CMD」？（唯讀查看類指令才可以）輸入 yes 繼續: " ans
            if [ "$ans" != "yes" ]; then
                log_warn "跳過 $h"
                continue
            fi
        fi
    fi
    if ! do_ssh "$h" "$CMD"; then
        log_error "$h 執行失敗（exit code $?）"
    fi
done
