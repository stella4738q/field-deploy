# Batch Process 批量管理脚本

## 📋 可用脚本

### 启动所有服务
```bash
./start_all_batch.sh
```
启动所有 batch process 服务（排除 `build_code` 和 `rapid_deploy`）

### 停止所有服务
```bash
./stop_all_batch.sh
```
停止所有 batch process 服务（排除 `build_code` 和 `rapid_deploy`）

### 重启所有服务
```bash
./restart_all_batch.sh
```
先停止再启动所有服务

## 📦 包含的服务

脚本会管理以下服务：

1. ✅ `essci_batch`
2. ✅ `job_00_status_control`
3. ✅ `job_01_protect_control`
4. ✅ `job_02_reverse_control`
5. ✅ `job_03_power_control`
6. ✅ `job_04_contract_power`
7. ✅ `job_05_charge_schedule`
8. ✅ `job_07_auto_charge`
9. ✅ `job_08_deadline`
10. ✅ `job_09_sr_process_control`
11. ✅ `job_90_report_generator`
12. ✅ `job_92_schedule_remove_data`
13. ✅ `job_94_alarm_notify`
14. ✅ `job_95_switch_tester`
15. ✅ `job_99_sr_process`

## ⛔ 排除的服务

- ❌ `build_code` - 构建代码目录
- ❌ `rapid_deploy` - 快速部署目录

## 🎯 使用示例

### 启动所有服务
```bash
cd /Users/chingjenchen/Dropbox/FEMC/Field\ Deploy/field-deploy/evergreen_yp/ems-server-1/batch_process

./start_all_batch.sh
```

### 停止所有服务
```bash
./stop_all_batch.sh
```

### 查看运行状态
```bash
docker ps | grep -E "(job_|essci_)"
```

### 查看特定服务日志
```bash
cd job_00_status_control
docker-compose logs -f
```

## 📊 脚本功能

### `start_all_batch.sh`
- ✅ 自动检测所有包含 docker-compose.yml 的目录
- ✅ 排除 build_code 和 rapid_deploy
- ✅ 依次启动所有服务
- ✅ 显示启动结果统计
- ✅ 列出失败的服务（如果有）

### `stop_all_batch.sh`
- ✅ 倒序停止所有服务
- ✅ 显示停止结果统计
- ✅ 确认所有容器已停止

### `restart_all_batch.sh`
- ✅ 先停止再启动
- ✅ 中间等待 3 秒

## 🔧 高级用法

### 只启动特定服务
```bash
cd job_00_status_control
docker-compose up -d
```

### 只停止特定服务
```bash
cd job_00_status_control
docker-compose down
```

### 查看所有服务状态
```bash
for dir in job_* essci_batch; do
    echo "=== $dir ==="
    cd "$dir" && docker-compose ps && cd ..
done
```

### 重新构建并启动
```bash
cd job_00_status_control
docker-compose up -d --build
```

## 📝 注意事项

1. 确保 Docker 已安装并运行
2. 确保有足够的系统资源运行所有容器
3. 某些服务可能有依赖关系，注意启动顺序
4. 查看日志排查问题：`docker-compose logs -f`

## 🐛 故障排除

### 问题：某些服务启动失败

```bash
# 查看具体服务日志
cd <服务目录>
docker-compose logs

# 检查配置文件
cat docker-compose.yml
cat config.ini
```

### 问题：端口冲突

```bash
# 查看端口占用
lsof -i :<端口号>

# 停止占用端口的服务
docker-compose down
```

### 问题：容器无法启动

```bash
# 查看详细错误
docker-compose up

# 重新构建镜像
docker-compose up -d --build
```

## 📂 目录结构

```
batch_process/
├── start_all_batch.sh      ← 启动脚本
├── stop_all_batch.sh       ← 停止脚本
├── restart_all_batch.sh    ← 重启脚本
├── README.md              ← 本文档
├── essci_batch/
│   └── docker-compose.yml
├── job_00_status_control/
│   └── docker-compose.yml
├── job_01_protect_control/
│   └── docker-compose.yml
...
└── job_99_sr_process/
    └── docker-compose.yml
```

