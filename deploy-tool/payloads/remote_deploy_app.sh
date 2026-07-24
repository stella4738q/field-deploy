#!/bin/bash
set -e
TARGET_DIR="$1"
echo "===== [remote] 部署: $(hostname) → $TARGET_DIR ====="

if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
fi

FAIL=0
for compose in $(find "$TARGET_DIR" -name docker-compose.yml | sort); do
    d=$(dirname "$compose")
    echo ""
    echo "--- docker compose up: $d ---"
    if (cd "$d" && docker compose up -d); then
        echo "✓ $d 啟動成功"
    else
        echo "✗ $d 啟動失敗"
        FAIL=1
    fi
done

echo ""
echo "--- 容器狀態 ---"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
exit $FAIL
