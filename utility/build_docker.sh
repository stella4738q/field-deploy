#!/bin/bash

# Femc Modbus Reader - Docker 構建和推送腳本

set -e  # 遇到錯誤立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函數：打印消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 顯示使用方式
usage() {
    cat << EOF
使用方式: $0 [版本] [選項]

位置參數:
  VERSION                    版本標籤（默認: latest 或 git tag）

選項:
  -u, --username USERNAME    Docker Hub 用戶名（默認: femc）
  -i, --image IMAGE_NAME     映像名稱
  -f, --file PATH            Dockerfile 路徑或目錄（默認: ./Dockerfile）
                             如果是目錄，會自動使用該目錄下的 Dockerfile
  -p, --push                 自動推送到 Docker Hub（不詢問）
  -m, --multi-platform       構建多平台映像（arm64, amd64）
  -h, --help                 顯示此幫助訊息

環境變數:
  DOCKER_USERNAME            Docker Hub 用戶名

範例:
  $0 v1.0.0
  $0 v1.0.0 -u femc
  $0 v1.0.0 --username femc --push
  $0 v1.0.0 --file ./docker/Dockerfile
  $0 v1.0.0 -f ./path/to/project/          # 使用目錄路徑
  $0 v1.0.0 -f Dockerfile.prod --multi-platform --push
  DOCKER_USERNAME=femc $0 v1.0.0
EOF
    exit 1
}

# 默認值
AUTO_PUSH=false
MULTI_PLATFORM=false
VERSION=""
DOCKERFILE_PATH="./Dockerfile"
REPLY=""

# 解析命令行參數
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--username)
            DOCKER_USERNAME="$2"
            shift 2
            ;;
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -f|--file)
            DOCKERFILE_PATH="$2"
            shift 2
            ;;
        -p|--push)
            AUTO_PUSH=true
            shift
            ;;
        -m|--multi-platform)
            MULTI_PLATFORM=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "未知選項: $1"
            usage
            ;;
        *)
            VERSION="$1"
            shift
            ;;
    esac
done

# 處理 Dockerfile 路徑
# 如果指定的是目錄，自動添加 /Dockerfile
if [ -d "$DOCKERFILE_PATH" ]; then
    DOCKERFILE_PATH="${DOCKERFILE_PATH%/}/Dockerfile"
    print_message "檢測到目錄，使用 Dockerfile: ${DOCKERFILE_PATH}"
fi

# 檢查 Dockerfile 是否存在
if [ ! -f "$DOCKERFILE_PATH" ]; then
    print_error "Dockerfile 不存在: ${DOCKERFILE_PATH}"
    exit 1
fi

# 配置
DOCKER_USERNAME="${DOCKER_USERNAME:-femc}"
IMAGE_NAME="${IMAGE_NAME:-}"
DOCKER_IMAGE="${DOCKER_USERNAME}/${IMAGE_NAME}"


# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安裝，請先安裝 Docker"
    exit 1
fi

# 獲取版本號
if [ -z "$VERSION" ]; then
    VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "latest")
fi

print_message "開始構建 Docker 映像..."
print_message "Docker 用戶名: ${DOCKER_USERNAME}"
print_message "映像名稱: ${IMAGE_NAME}"
print_message "版本: ${VERSION}"
print_message "Dockerfile 路徑: ${DOCKERFILE_PATH}"
print_message "完整映像: ${DOCKER_IMAGE}"

# 如果啟用多平台構建，檢查並設置 buildx
if [ "$MULTI_PLATFORM" = true ]; then
    print_message "啟用多平台構建模式（arm64, amd64）"

    # 檢查 buildx 是否可用
    if ! docker buildx version &> /dev/null; then
        print_error "Docker buildx 不可用，請確保使用最新版本的 Docker"
        exit 1
    fi

    # 創建或使用 buildx builder
    BUILDER_NAME="femc-multiplatform-builder"
    if ! docker buildx inspect $BUILDER_NAME &> /dev/null; then
        print_message "創建 buildx builder: $BUILDER_NAME"
        docker buildx create --name $BUILDER_NAME --use
    else
        print_message "使用現有的 buildx builder: $BUILDER_NAME"
        docker buildx use $BUILDER_NAME
    fi

    # 啟動 builder
    docker buildx inspect --bootstrap
fi

# 構建映像
print_message "構建映像..."

# 確定構建上下文和 Dockerfile 路徑
# 如果 Dockerfile 路徑是絕對路徑或包含目錄，需要處理構建上下文
if [[ "$DOCKERFILE_PATH" == /* ]] || [[ "$DOCKERFILE_PATH" == */* ]]; then
    # 獲取 Dockerfile 所在目錄作為構建上下文
    BUILD_CONTEXT="$(dirname "$DOCKERFILE_PATH")"
    # 對於 docker buildx，使用原始的 DOCKERFILE_PATH（相對於當前目錄）
    DOCKERFILE_FOR_BUILD="$DOCKERFILE_PATH"
    print_message "構建上下文: ${BUILD_CONTEXT}"
    print_message "Dockerfile: ${DOCKERFILE_PATH}"
else
    # 使用當前目錄作為構建上下文
    BUILD_CONTEXT="."
    DOCKERFILE_FOR_BUILD="$DOCKERFILE_PATH"
fi

if [ "$MULTI_PLATFORM" = true ]; then
    # 多平台構建
    if [ "$AUTO_PUSH" = true ]; then
        # 多平台構建並推送到 registry
        print_message "多平台構建，將直接推送到 Docker Hub..."
        docker login

        docker buildx build \
            --platform linux/arm64,linux/amd64 \
            --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
            --build-arg VERSION=${VERSION} \
            -t ${DOCKER_IMAGE}:${VERSION} \
            -t ${DOCKER_IMAGE}:latest \
            -f ${DOCKERFILE_FOR_BUILD} \
            --push \
            ${BUILD_CONTEXT}
    else
        # 多平台構建但只加載當前平台到本地
        print_warning "多平台構建模式下，將只加載當前平台的映像到本地 Docker"
        print_warning "如需構建並推送所有平台，請使用 -p 或 --push 選項"

        # 偵測當前平台
        CURRENT_PLATFORM=$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')
        print_message "當前平台: ${CURRENT_PLATFORM}"

        docker buildx build \
            --platform ${CURRENT_PLATFORM} \
            --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
            --build-arg VERSION=${VERSION} \
            -t ${DOCKER_IMAGE}:${VERSION} \
            -t ${DOCKER_IMAGE}:latest \
            -f ${DOCKERFILE_FOR_BUILD} \
            --load \
            ${BUILD_CONTEXT}
    fi
else
    # 單平台構建（原有邏輯）
    docker build \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VERSION=${VERSION} \
        -t ${DOCKER_IMAGE}:${VERSION} \
        -t ${DOCKER_IMAGE}:latest \
        -f ${DOCKERFILE_FOR_BUILD} \
        ${BUILD_CONTEXT}
fi

if [ $? -eq 0 ]; then
    print_message "✅ 映像構建成功"
else
    print_error "❌ 映像構建失敗"
    exit 1
fi

# 詢問是否推送到 Docker Hub
# 如果是多平台構建且已經推送，跳過這一步
if [ "$MULTI_PLATFORM" = true ] && [ "$AUTO_PUSH" = true ]; then
    print_message "多平台映像已推送到 Docker Hub"
    print_message "映像已推送: ${DOCKER_IMAGE}:${VERSION}"
    print_message "映像已推送: ${DOCKER_IMAGE}:latest"
elif [ "$AUTO_PUSH" = true ]; then
    # 單平台構建且啟用自動推送
    print_message "登入 Docker Hub..."
    docker login

    if [ $? -eq 0 ]; then
        print_message "推送映像 ${DOCKER_IMAGE}:${VERSION}..."
        docker push ${DOCKER_IMAGE}:${VERSION}

        print_message "推送映像 ${DOCKER_IMAGE}:latest..."
        docker push ${DOCKER_IMAGE}:latest

        print_message "✅ 映像推送成功"
        print_message "映像已推送: ${DOCKER_IMAGE}:${VERSION}"
        print_message "映像已推送: ${DOCKER_IMAGE}:latest"
    else
        print_error "❌ Docker Hub 登入失敗"
        exit 1
    fi
else
    # 詢問用戶是否推送
    read -p "是否要推送映像到 Docker Hub? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message "登入 Docker Hub..."
        docker login

        if [ $? -eq 0 ]; then
            print_message "推送映像 ${DOCKER_IMAGE}:${VERSION}..."
            docker push ${DOCKER_IMAGE}:${VERSION}

            print_message "推送映像 ${DOCKER_IMAGE}:latest..."
            docker push ${DOCKER_IMAGE}:latest

            print_message "✅ 映像推送成功"
            print_message "映像已推送: ${DOCKER_IMAGE}:${VERSION}"
            print_message "映像已推送: ${DOCKER_IMAGE}:latest"
        else
            print_error "❌ Docker Hub 登入失敗"
            exit 1
        fi
    fi
fi

# 顯示映像信息
if [ "$MULTI_PLATFORM" = true ] && [ "$AUTO_PUSH" = true ]; then
    print_message "映像已推送到 Docker Hub，可以使用以下命令查看詳細資訊:"
    print_message "  docker buildx imagetools inspect ${DOCKER_IMAGE}:${VERSION}"
else
    print_message "本地映像信息:"
    docker images | head -1
    docker images | grep ${IMAGE_NAME} || print_warning "未找到本地映像"
fi

print_message "🎉 完成!"

