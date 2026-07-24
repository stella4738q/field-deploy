#!/bin/bash
# 推送檔案/目錄到目標主機：./push.sh [--dry-run] <name> <本地路徑> <遠端路徑>
# readonly 主機一律拒絕
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

parse_dry_run "$@"
set -- "${ARGS[@]}"

if [ $# -lt 3 ]; then
    echo "使用方式: $0 [--dry-run] <name> <本地路徑> <遠端路徑>"
    echo "範例:  $0 jy-ems1 ../ems-server-1/ '~/deploy/ems-server-1/'"
    exit 1
fi

NAME="$1"; SRC="$2"; DST="$3"

assert_writable "$NAME"

if [ ! -e "$SRC" ]; then
    log_error "本地路徑不存在: $SRC"
    exit 1
fi

log_info "即將推送:"
log_info "  來源: $SRC"
log_info "  目標: ${NAME}（$(ssh_dest "$NAME") port $(ssh_port "$NAME")）:$DST"
confirm "確認推送？"

do_rsync "$NAME" "$SRC" "$DST"
log_info "✓ 推送完成"
