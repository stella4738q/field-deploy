# FEMC EMS 多容器网络配置说明

## 概述

这个配置使用 **外部共享网络（external network）** 来连接四个独立的 Docker Compose 项目：

1. **evergreen_yp_ems_website** - 前端网站 (容器名: `web-app`)
2. **evergreen_yp_ems_backend_api_local** - 后端 API (容器名: `web-api`)
3. **evergreen_yp_ems_web_socket_server** - WebSocket 服务器 (容器名: `web-socket-server`)
4. **reverse_proxy** - Nginx 反向代理 (容器名: `reverse_proxy`)

所有容器都连接到同一个外部网络：`femc_ems_network`

## 快速开始

### 1. 创建共享网络

在启动任何容器之前，必须先创建共享网络：

```bash
# 方法 1: 使用管理脚本
./scripts/manage_network.sh create

# 方法 2: 手动创建
docker network create femc_ems_network
```

### 2. 启动所有服务

按以下顺序启动服务（推荐）：

```bash
# 1. 启动后端 API
cd evergreen_yp_ems_backend_api_local
docker-compose up -d

# 2. 启动 WebSocket 服务器
cd ../evergreen_yp_ems_web_socket_server
docker-compose up -d

# 3. 启动前端网站
cd ../evergreen_yp_ems_website
docker-compose up -d

# 4. 启动反向代理
cd ../reverse_proxy
docker-compose up -d
```

或者使用一键启动脚本：

```bash
./scripts/start_all.sh
```

### 3. 验证网络连接

```bash
# 检查网络状态
./scripts/manage_network.sh check

# 列出所有连接的容器
./scripts/manage_network.sh list

# 查看网络详细信息
./scripts/manage_network.sh info
```

## 容器间通信

容器可以通过以下名称互相访问：

- **web-app** (端口 80) - 前端网站
- **web-api** (端口 5000) - 后端 API
- **web-socket-server** (端口 8009) - WebSocket 服务
- **reverse_proxy** (端口 80) - 反向代理

### 示例：

```bash
# 在 reverse_proxy 容器中访问后端 API
curl http://web-api:5000/api/health

# 在任何容器中访问 WebSocket
ws://web-socket-server:8009
```

## Nginx 反向代理配置

反向代理配置在 `reverse_proxy/nginx.conf` 和 `reverse_proxy/configs/*.locations` 中：

- `/` → `web-app:80` (前端)
- `/api/*` → `web-api:5000` (后端 API)
- `/socket` → `web-socket-server:8009` (WebSocket)

## 管理命令

### 启动服务

```bash
# 启动单个服务
cd <service_directory>
docker-compose up -d

# 启动所有服务
./scripts/start_all.sh
```

### 停止服务

```bash
# 停止单个服务
cd <service_directory>
docker-compose down

# 停止所有服务
./scripts/stop_all.sh
```

### 查看日志

```bash
# 查看单个服务日志
cd <service_directory>
docker-compose logs -f

# 查看所有容器日志
docker-compose -f evergreen_yp_ems_backend_api_local/docker-compose.yml \
               -f evergreen_yp_ems_web_socket_server/docker-compose.yml \
               -f evergreen_yp_ems_website/docker-compose.yml \
               -f reverse_proxy/docker-compose.yml \
               logs -f
```

### 重启服务

```bash
# 重启单个服务
cd <service_directory>
docker-compose restart

# 重新构建并重启
docker-compose up -d --build
```

## 网络管理

### 管理脚本命令

```bash
./scripts/manage_network.sh create   # 创建网络
./scripts/manage_network.sh remove   # 删除网络
./scripts/manage_network.sh info     # 查看网络详细信息
./scripts/manage_network.sh list     # 列出连接的容器
./scripts/manage_network.sh check    # 检查网络状态
```

### 手动网络命令

```bash
# 创建网络
docker network create femc_ems_network

# 删除网络（需要先停止所有容器）
docker network rm femc_ems_network

# 查看网络信息
docker network inspect femc_ems_network

# 列出所有网络
docker network ls
```

## 故障排除

### 问题 1: 网络不存在

**错误信息：**
```
ERROR: Network femc_ems_network declared as external, but could not be found
```

**解决方法：**
```bash
./scripts/manage_network.sh create
```

### 问题 2: 容器无法互相通信

**检查步骤：**

1. 确认所有容器都在同一个网络中：
```bash
./scripts/manage_network.sh list
```

2. 测试容器间连接：
```bash
# 进入 reverse_proxy 容器
docker exec -it reverse_proxy sh

# 测试连接其他容器
ping web-app
ping web-api
ping web-socket-server
```

3. 检查容器日志：
```bash
docker logs reverse_proxy
docker logs web-api
docker logs web-socket-server
docker logs web-app
```

### 问题 3: 端口冲突

**检查端口占用：**
```bash
# 检查 80 端口
lsof -i :80

# 检查 8009 端口
lsof -i :8009
```

### 问题 4: 无法删除网络

**错误信息：**
```
Error response from daemon: network femc_ems_network has active endpoints
```

**解决方法：**
```bash
# 停止所有使用该网络的容器
cd evergreen_yp_ems_backend_api_local && docker-compose down
cd ../evergreen_yp_ems_web_socket_server && docker-compose down
cd ../evergreen_yp_ems_website && docker-compose down
cd ../reverse_proxy && docker-compose down

# 然后删除网络
./scripts/manage_network.sh remove
```

## 架构图

```
                    ┌─────────────────────────────┐
                    │   Docker Network:           │
                    │   femc_ems_network          │
                    └─────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        │                        │                        │
   ┌────▼────┐            ┌─────▼─────┐          ┌──────▼──────┐
   │ web-app │            │  web-api  │          │ web-socket- │
   │  :80    │            │  :5000    │          │  server     │
   └─────────┘            └───────────┘          │  :8009      │
        ▲                        ▲                └─────────────┘
        │                        │                       ▲
        │                        │                       │
        └────────────────────────┴───────────────────────┘
                                 │
                         ┌───────▼────────┐
                         │ reverse_proxy  │
                         │     :80        │
                         └────────────────┘
                                 │
                         ┌───────▼────────┐
                         │  外部访问      │
                         │ localhost:80   │
                         └────────────────┘
```

## 配置文件位置

```
femc_ems/
├── manage_network.sh                    # 网络管理脚本
├── start_all.sh                         # 启动所有服务
├── stop_all.sh                          # 停止所有服务
├── README.md                            # 本文档
├── evergreen_yp_ems_website/
│   └── docker-compose.yml
├── evergreen_yp_ems_backend_api_local/
│   └── docker-compose.yml
├── evergreen_yp_ems_web_socket_server/
│   └── docker-compose.yml
└── reverse_proxy/
    ├── docker-compose.yml
    ├── nginx.conf
    └── configs/
        ├── web-api.locations
        └── web-socket.locations
```

## 注意事项

1. **必须先创建网络** - 在启动任何容器之前，必须先创建 `femc_ems_network`
2. **容器名称一致性** - 确保 nginx 配置中使用的容器名称与 docker-compose.yml 中定义的一致
3. **启动顺序** - 建议按照依赖顺序启动：API → WebSocket → Frontend → Proxy
4. **网络隔离** - 只有在同一网络中的容器才能互相通信
5. **端口映射** - reverse_proxy 是唯一需要暴露到主机的服务（端口 80）

