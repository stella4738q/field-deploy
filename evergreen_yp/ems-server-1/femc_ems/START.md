# 🚀 FEMC EMS 快速启动命令

## 最简单的方式（推荐）

```bash
cd /Users/chingjenchen/Dropbox/FEMC/Field\ Deploy/field-deploy/evergreen_yp/ems-server-1/femc_ems

./scripts/start_all.sh
```

✅ 脚本会自动：
- 创建网络
- 检测可用服务
- 配置 nginx
- 启动所有容器

## 访问网站

打开浏览器访问：**http://localhost** 或 **http://127.0.0.1**

## 停止服务

```bash
./scripts/stop_all.sh
```

## 查看状态

```bash
# 查看运行中的容器
docker ps

# 查看日志
docker logs web-app
docker logs reverse_proxy

# 测试网络连接
./script./scripts/test_network.sh
```

## 如果遇到问题

### 问题：网页无法访问

```bash
# 1. 检查容器状态
docker ps

# 2. 查看 reverse_proxy 日志
docker logs reverse_proxy

# 3. 如果 reverse_proxy 一直重启，手动修复：
cd reverse_proxy/configs
mv web-api.locations web-api.locations.disabled 2>/dev/null || true
mv web-socket.locations web-socket.locations.disabled 2>/dev/null || true
mv relay-api.locations relay-api.locations.disabled 2>/dev/null || true
cd .. && docker-compose restart
```

### 问题：端口被占用

```bash
# 查看占用端口 80 的进程
lsof -i :80

# 停止占用的进程或修改端口
```

### 问题：网络不存在

```bash
docker network create femc_ems_network
```

## 详细文档

- **完整启动指南**: `cat STARTUP_GUIDE.md`
- **网络说明**: `cat NETWORK_GUIDE.md`
- **快速参考**: `cat QUICKSTART.md`

---

**当前配置**：
- 前端：web-app (必须)
- 反向代理：reverse_proxy (必须)
- 后端 API：web-api (可选)
- WebSocket：web-socket-server (可选)

