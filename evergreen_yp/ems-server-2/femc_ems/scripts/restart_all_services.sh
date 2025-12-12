#!/bin/bash

# 重啟所有 EMS 服務的腳本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "重啟 EMS 服務"
echo "=========================================="

# 先停止所有服務
"$SCRIPT_DIR/stop_all_services.sh"

echo ""
echo "等待 2 秒..."
sleep 2

# 再啟動所有服務
"$SCRIPT_DIR/start_all_services.sh"

