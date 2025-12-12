#!/bin/bash
# 恢复 reverse_proxy configs 配置文件

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 脚本在 scripts/ 目录，需要返回上一级
PARENT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
CONFIG_DIR="$PARENT_DIR/reverse_proxy/configs"

cd "$CONFIG_DIR"

print_info "当前目录: $CONFIG_DIR"
echo ""

# 显示使用方法
usage() {
    echo "使用方式: $0 [选项] [配置名称]"
    echo ""
    echo "选项:"
    echo "  all              恢复所有配置文件"
    echo "  web-api          恢复 web-api 配置"
    echo "  web-socket       恢复 web-socket 配置"
    echo "  relay-api        恢复 relay-api 配置"
    echo "  tjs-3d           恢复 tjs-3d 配置"
    echo "  list             列出所有可恢复的配置"
    echo "  -h, --help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 all                    # 恢复所有配置"
    echo "  $0 web-api                # 只恢复 web-api 配置"
    echo "  $0 web-api web-socket     # 恢复多个配置"
    echo ""
    exit 0
}

# 列出可恢复的配置
list_configs() {
    echo "可恢复的配置文件:"
    echo ""
    for file in *.disabled; do
        if [ -f "$file" ]; then
            original_name="${file%.disabled}"
            echo "  ✗ $original_name (已禁用)"
        fi
    done
    echo ""
    echo "当前启用的配置:"
    echo ""
    for file in *.locations; do
        if [ -f "$file" ]; then
            echo "  ✓ ${file%.locations}"
        fi
    done
    if ! ls *.locations 1> /dev/null 2>&1; then
        echo "  (无)"
    fi
}

# 恢复单个配置
restore_config() {
    local config_name=$1
    local file_pattern=""

    case $config_name in
        web-api)
            file_pattern="web-api.locations"
            ;;
        web-socket|websocket)
            file_pattern="web-socket.locations"
            ;;
        relay-api|relay)
            file_pattern="relay-api.locations"
            ;;
        tjs-3d|tjs)
            file_pattern="tjs-3d.locations"
            ;;
        *)
            print_error "未知的配置名称: $config_name"
            return 1
            ;;
    esac

    if [ -f "${file_pattern}.disabled" ]; then
        mv "${file_pattern}.disabled" "${file_pattern}"
        print_message "已恢复: $file_pattern"
        return 0
    elif [ -f "${file_pattern}" ]; then
        print_warning "$file_pattern 已经启用，跳过"
        return 0
    else
        print_error "找不到文件: ${file_pattern}.disabled"
        return 1
    fi
}

# 恢复所有配置
restore_all() {
    local count=0
    for file in *.disabled; do
        if [ -f "$file" ]; then
            original_name="${file%.disabled}"
            mv "$file" "$original_name"
            print_message "已恢复: $original_name"
            ((count++))
        fi
    done

    if [ $count -eq 0 ]; then
        print_warning "没有需要恢复的配置文件"
    else
        print_message "共恢复了 $count 个配置文件"
    fi
}

# 主程序
if [ $# -eq 0 ]; then
    print_info "请指定要恢复的配置"
    echo ""
    list_configs
    echo ""
    print_info "使用 '$0 --help' 查看帮助"
    exit 0
fi

case "${1}" in
    -h|--help|help)
        usage
        ;;
    list|ls)
        list_configs
        ;;
    all)
        echo "恢复所有配置文件..."
        echo ""
        restore_all
        echo ""
        print_info "完成！请重启 reverse_proxy:"
        echo "  cd ../.. && docker-compose restart"
        ;;
    *)
        echo "恢复指定的配置文件..."
        echo ""
        success_count=0
        for config in "$@"; do
            if restore_config "$config"; then
                ((success_count++))
            fi
        done
        echo ""
        if [ $success_count -gt 0 ]; then
            print_message "共恢复了 $success_count 个配置文件"
            echo ""
            print_info "完成！请重启 reverse_proxy:"
            echo "  cd .. && docker-compose restart"
        fi
        ;;
esac

