# FEMC EMS 文档索引

欢迎使用 FEMC EMS 系统！这里是所有文档的快速索引。

## 🚀 快速开始

**新手？从这里开始：**
- [**START.md**](START.md) - 最简单的一页快速启动指南 ⭐ **推荐新手阅读**

## 📚 主要文档

### 启动和配置
- [**QUICKSTART.md**](QUICKSTART.md) - 快速参考手册
- [**STARTUP_GUIDE.md**](STARTUP_GUIDE.md) - 完整详细的启动指南
- [**RESTORE_CONFIG.md**](RESTORE_CONFIG.md) - 配置恢复详细说明
- [**HOW_TO_RESTORE.md**](HOW_TO_RESTORE.md) - 配置恢复快速指南

### 网络和架构
- [**NETWORK_GUIDE.md**](NETWORK_GUIDE.md) - Docker 网络架构详解
- [**README.md**](README.md) - 系统完整说明文档

### 变更说明
- [**SCRIPTS_MIGRATION.md**](SCRIPTS_MIGRATION.md) - 脚本迁移说明

## 🛠️ 脚本工具

所有脚本位于 `scripts/` 目录：

### 启动和停止
```bash
./scripts/start_all.sh      # 一键启动所有服务
./scripts/stop_all.sh       # 一键停止所有服务
```

### 网络管理
```bash
./scripts/manage_network.sh create    # 创建共享网络
./scripts/manage_network.sh check     # 检查网络状态
./scripts/manage_network.sh list      # 列出网络中的容器
./scripts/manage_network.sh info      # 查看网络详细信息
./scripts/manage_network.sh remove    # 删除网络
```

### 配置管理
```bash
./scripts/restore_configs.sh list         # 查看配置状态
./scripts/restore_configs.sh all          # 恢复所有配置
./scripts/restore_configs.sh web-api      # 恢复指定配置
```

### 测试和诊断
```bash
./scripts/test_network.sh    # 测试网络连接性
```

## 📖 按任务查找文档

### 我想要...

**...第一次启动系统**
→ 阅读 [START.md](START.md)

**...了解完整的启动流程**
→ 阅读 [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

**...恢复 nginx 配置**
→ 阅读 [HOW_TO_RESTORE.md](HOW_TO_RESTORE.md)

**...理解网络架构**
→ 阅读 [NETWORK_GUIDE.md](NETWORK_GUIDE.md)

**...快速查找命令**
→ 阅读 [QUICKSTART.md](QUICKSTART.md)

**...排查网络问题**
→ 运行 `./scripts/test_network.sh` 然后查看 [NETWORK_GUIDE.md](NETWORK_GUIDE.md)

**...了解脚本位置变更**
→ 阅读 [SCRIPTS_MIGRATION.md](SCRIPTS_MIGRATION.md)

## 🎯 常用命令速查

```bash
# 快速启动
cd /Users/chingjenchen/Dropbox/FEMC/Field\ Deploy/field-deploy/evergreen_yp/ems-server-1/femc_ems
./scripts/start_all.sh

# 查看状态
docker ps
./scripts/manage_network.sh list

# 查看日志
docker logs web-app
docker logs reverse_proxy

# 停止服务
./scripts/stop_all.sh

# 测试网络
./scripts/test_network.sh

# 恢复配置
./scripts/restore_configs.sh list
./scripts/restore_configs.sh all
```

## 📁 文件结构

```
femc_ems/
├── scripts/                    ← 所有可执行脚本
│   ├── start_all.sh
│   ├── stop_all.sh
│   ├── manage_network.sh
│   ├── restore_configs.sh
│   └── test_network.sh
├── START.md                    ← 快速入门
├── QUICKSTART.md               ← 快速参考
├── STARTUP_GUIDE.md           ← 完整启动指南
├── NETWORK_GUIDE.md           ← 网络架构
├── RESTORE_CONFIG.md          ← 配置恢复详解
├── HOW_TO_RESTORE.md          ← 配置恢复快速指南
├── README.md                   ← 系统完整说明
├── SCRIPTS_MIGRATION.md       ← 脚本迁移说明
└── INDEX.md                    ← 本文档
```

## 🆘 需要帮助？

1. 先查看 [START.md](START.md) 快速入门
2. 遇到问题查看对应的详细文档
3. 运行 `./scripts/test_network.sh` 诊断网络问题
4. 查看容器日志：`docker logs <container_name>`

## 🔗 快速链接

- 访问系统：http://localhost
- WebSocket（如果启用）：ws://localhost:8009
- 后端 API（如果启用）：http://localhost/api/

