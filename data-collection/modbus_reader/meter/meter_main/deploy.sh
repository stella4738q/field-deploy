#!/bin/bash

# FEMC Modbus Reader 部署腳本
# 用途：建構 Docker 映像並部署應用程式

set -e  # 遇到錯誤時立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置變數
IMAGE_NAME="femc-modbus-reader"
CONTAINER_NAME="modbus-reader"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VERSION="${VERSION:-latest}"
DOCKER_HUB_REPO="${DOCKER_HUB_REPO:-femc/femc-modbus-reader}"  # Docker Hub 儲存庫名稱（格式：username/repository）
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_USERNAME="${DOCKER_USERNAME:-femc}"  # Docker Hub 使用者名稱
DOCKER_PASSWORD="${DOCKER_PASSWORD:-}"  # Docker Hub 密碼或 access token

# 函數：印出帶顏色的訊息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函數：檢查必要目錄
check_directories() {
    log_info "檢查必要目錄..."

    local dirs=("config" "modbus_config" "plugins" "logs")
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log_warn "目錄 $dir 不存在，正在創建..."
            mkdir -p "$dir"
        fi
    done
}

# 函數：登入 Docker Hub
docker_login() {
    log_info "檢查 Docker Hub 登入狀態..."

    # 如果已經登入，跳過
    if docker info 2>/dev/null | grep -q "Username"; then
        local current_user=$(docker info 2>/dev/null | grep "Username" | awk '{print $2}')
        log_info "已登入 Docker Hub (使用者: $current_user)"
        return 0
    fi

    # 檢查是否提供了登入憑證
    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        log_info "使用環境變數登入 Docker Hub (使用者: $DOCKER_USERNAME)..."

        # 暫時停用 set -e 以便處理登入錯誤
        set +e
        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
        local login_result=$?
        set -e

        if [ $login_result -eq 0 ]; then
            log_info "Docker Hub 登入成功"
            return 0
        else
            log_error "Docker Hub 登入失敗，請檢查使用者名稱和密碼"
            return 1
        fi
    else
        # 互動式登入
        log_warn "未提供 DOCKER_USERNAME 和 DOCKER_PASSWORD 環境變數"
        log_info "進入互動式登入模式..."
        echo ""

        # 暫時停用 set -e 以便處理登入錯誤
        set +e
        docker login
        local login_result=$?
        set -e

        echo ""
        if [ $login_result -eq 0 ]; then
            log_info "Docker Hub 登入成功"
            return 0
        else
            log_error "Docker Hub 登入失敗或已取消"
            return 1
        fi
    fi
}

# 函數：停止並移除舊容器
stop_and_remove_container() {
    log_info "檢查是否有運行中的容器..."

    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        log_warn "停止運行中的容器: $CONTAINER_NAME"
        docker stop $CONTAINER_NAME
    fi

    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        log_warn "移除舊容器: $CONTAINER_NAME"
        docker rm $CONTAINER_NAME
    fi
}

# 函數：清理舊映像（可選）
cleanup_old_images() {
    log_info "清理未使用的 Docker 映像..."
    docker image prune -f
}

# 函數：從 Docker Hub pull image
pull_image_from_hub() {
    local hub_image="${DOCKER_HUB_REPO}:${VERSION}"


    log_info "從 Docker Hub pull 映像: $hub_image"

    # 暫時停用 set -e 以便處理 pull 錯誤
    set +e
    docker pull "$hub_image"
    local pull_result=$?
    set -e

    if [ $pull_result -eq 0 ]; then
        log_info "成功 pull 映像: $hub_image"

        # 重新標記為本地映像名稱
        log_info "重新標記映像為: $IMAGE_NAME:$VERSION"
        docker tag "$hub_image" "$IMAGE_NAME:$VERSION"
        docker tag "$hub_image" "$IMAGE_NAME:latest"

        return 0
    else
        log_error "Pull 映像失敗: $hub_image"
        log_error "請檢查："
        log_error "  1. 映像名稱是否正確"
        log_error "  2. 版本標籤是否存在"
        log_error "  3. 如果是私有倉庫，是否已正確登入"
        return 1
    fi
}

# 函數：更新 docker-compose.yml 中的 image
update_compose_image() {
    local new_image="${IMAGE_NAME}:${VERSION}"

    log_info "更新 docker-compose.yml 中的映像為: $new_image"

    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "找不到 $DOCKER_COMPOSE_FILE 文件！"
        return 1
    fi

    # 備份原始文件
    cp "$DOCKER_COMPOSE_FILE" "${DOCKER_COMPOSE_FILE}.bak"
    log_info "已備份 docker-compose.yml 至 ${DOCKER_COMPOSE_FILE}.bak"

    # 使用 sed 更新 image 行（macOS 和 Linux 兼容）
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|image:.*|image: \"$new_image\"|g" "$DOCKER_COMPOSE_FILE"
    else
        # Linux
        sed -i "s|image:.*|image: \"$new_image\"|g" "$DOCKER_COMPOSE_FILE"
    fi

    log_info "docker-compose.yml 更新完成"
}

# 函數：建構 Docker 映像
build_image() {
    log_info "開始建構 Docker 映像: $IMAGE_NAME:$VERSION"

    docker build \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg VERSION="$VERSION" \
        -t "$IMAGE_NAME:$VERSION" \
        -t "$IMAGE_NAME:latest" \
        .

    if [ $? -eq 0 ]; then
        log_info "Docker 映像建構成功！"
    else
        log_error "Docker 映像建構失敗！"
        exit 1
    fi
}

# 函數：使用 docker-compose 部署
deploy_with_compose() {
    log_info "使用 docker compose 部署應用程式..."

    docker compose up -d

    if [ $? -eq 0 ]; then
        log_info "應用程式部署成功！"
    else
        log_error "應用程式部署失敗！"
        exit 1
    fi
}

# 函數：直接使用 docker run 部署（替代方案）
deploy_with_docker() {
    log_info "使用 docker run 部署應用程式..."

    docker run -d \
        --name $CONTAINER_NAME \
        --restart always \
        --network host \
        -v "$(pwd)/config:/app/config" \
        -v "$(pwd)/modbus_config:/app/modbus_config" \
        -v "$(pwd)/plugins:/app/plugins" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -e TZ=Asia/Taipei \
        "$IMAGE_NAME:$VERSION"

    if [ $? -eq 0 ]; then
        log_info "應用程式部署成功！"
    else
        log_error "應用程式部署失敗！"
        exit 1
    fi
}

# 函數：顯示容器狀態
show_status() {
    log_info "容器狀態："
    docker ps -f name=$CONTAINER_NAME

    echo ""
    log_info "查看日誌指令："
    echo "  docker logs -f $CONTAINER_NAME"
    echo ""
    log_info "進入容器指令："
    echo "  docker exec -it $CONTAINER_NAME /bin/bash"
}

# 函數：顯示使用說明
show_usage() {
    cat << EOF
使用方法: $0 [選項]

選項:
    build           只建構 Docker 映像
    pull            從 Docker Hub pull 映像並更新 docker-compose.yml
    deploy          只部署（使用現有映像）
    compose         使用 docker-compose 部署
    rebuild         重新建構並部署
    pull-deploy     從 Docker Hub pull 映像並自動部署
    login           登入 Docker Hub
    stop            停止容器
    restart         重啟容器
    logs            查看日誌
    status          查看狀態
    clean           清理未使用的映像
    help            顯示此說明

環境變數:
    VERSION             指定映像版本（預設: latest）
    DOCKER_HUB_REPO     指定 Docker Hub 儲存庫（預設: femc-modbus-reader）
    DOCKER_USERNAME     Docker Hub 使用者名稱（用於自動登入）
    DOCKER_PASSWORD     Docker Hub 密碼或 access token（用於自動登入）

範例:
    # 從 Docker Hub pull 並部署
    $0 pull-deploy

    # Pull 指定版本並部署
    VERSION=v1.0.0 $0 pull-deploy

    # 使用環境變數自動登入並 pull
    DOCKER_USERNAME=myuser DOCKER_PASSWORD=mytoken $0 pull-deploy

    # 從私有倉庫 pull（格式：username/repo）
    DOCKER_HUB_REPO=myuser/myrepo VERSION=v2.0.0 $0 pull-deploy

    # 手動登入 Docker Hub
    $0 login

    # 本地建構並部署
    $0 rebuild

    # 查看容器日誌
    $0 logs

EOF
}

# 主要執行流程
main() {
    local action="${1:-rebuild}"

    case "$action" in
        build)
            check_directories
            build_image
            ;;
        login)
            docker_login
            ;;
        pull)
            check_directories
            docker_login
            pull_image_from_hub
            update_compose_image
            log_info "映像已從 Docker Hub pull 並更新 docker-compose.yml"
            log_info "使用 '$0 deploy' 來部署應用程式"
            ;;
        pull-deploy)
            check_directories
            docker_login
            pull_image_from_hub
            update_compose_image
            stop_and_remove_container
            deploy_with_compose
            show_status
            ;;
        deploy)
            check_directories
            stop_and_remove_container
            deploy_with_compose
            show_status
            ;;
        compose)
            check_directories
            build_image
            stop_and_remove_container
            deploy_with_compose
            show_status
            ;;
        rebuild)
            check_directories
            build_image
            stop_and_remove_container
            deploy_with_compose
            show_status
            ;;
        stop)
            log_info "停止容器..."
            docker compose down
            ;;
        restart)
            log_info "重啟容器..."
            docker compose restart
            show_status
            ;;
        logs)
            docker logs -f $CONTAINER_NAME
            ;;
        status)
            show_status
            ;;
        clean)
            cleanup_old_images
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "未知的選項: $action"
            show_usage
            exit 1
            ;;
    esac
}

# 執行主程式
main "$@"

