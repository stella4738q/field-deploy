#!/bin/bash
# 快速連線到指定主機：./connect.sh <name>
set -e
source "$(cd "$(dirname "$0")" && pwd)/lib/common.sh"

if [ $# -lt 1 ] || [ "$1" = "--list" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "使用方式: $0 <name>"
    echo ""
    show_hosts_table
    exit 0
fi

NAME="$1"
if ! host_exists "$NAME"; then
    log_error "找不到主機: $NAME"
    echo ""
    show_hosts_table
    exit 1
fi

warn_if_readonly "$NAME"
log_info "連線到 ${NAME}（$(ssh_dest "$NAME") port $(ssh_port "$NAME")）..."
exec ssh -p "$(ssh_port "$NAME")" "$(ssh_dest "$NAME")"
