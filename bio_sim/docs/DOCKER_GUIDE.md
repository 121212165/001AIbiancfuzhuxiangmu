# Docker 快速使用指南

## 为什么使用Docker？

- ✅ **零依赖安装**: 不需要安装Python、PyGame等
- ✅ **环境隔离**: 不会影响本地系统
- ✅ **跨平台**: Windows/Mac/Linux统一体验
- ✅ **一键运行**: 简单命令即可启动

---

## 快速开始

### 1. 构建镜像（首次运行）

```bash
cd bio_sim
make build
```

这会下载Python基础镜像并安装所有依赖，**首次构建需要2-3分钟**。

### 2. 查看所有可用命令

```bash
make help
```

### 3. 运行模拟

```bash
# 方式1: 交互式菜单
make run

# 方式2: 直接运行特定模拟
make boids       # 群体行为模拟
make ecosystem   # 生态系统模拟
make life        # 生命游戏
make genetic     # 遗传算法
```

---

## 开发模式

### 启动开发容器

```bash
# 启动容器（后台运行）
make up

# 进入容器
make shell
```

现在你在容器内部，可以使用所有Python命令：

```bash
# 运行测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_boids.py -v

# 代码格式化
black .
isort .

# 代码检查
flake8 .
mypy core/
```

### 退出容器

```bash
exit
```

### 停止容器

```bash
make down
```

---

## 常用命令

### 构建相关
```bash
make build     # 构建镜像
make rebuild   # 重新构建（清除缓存）
```

### 运行相关
```bash
make run       # 运行主程序
make boids     # 运行Boids模拟
make ecosystem # 运行生态系统模拟
make life      # 运行生命游戏
make genetic   # 运行遗传算法
```

### 开发相关
```bash
make test      # 运行测试
make format    # 格式化代码
make lint      # 代码检查
```

### 清理
```bash
make clean     # 清理容器和镜像
```

---

## 实时开发流程

### 修改代码后立即看到效果

```bash
# 1. 启动开发容器
make up

# 2. 进入容器
make shell

# 3. 在容器内运行（容器内会实时看到你的代码修改）
python main.py
# 或
pytest tests/ -v

# 4. 修改代码（在本地编辑器修改）
# 容器内会立即看到变化（因为使用了volume挂载）
```

---

## Docker Compose 直接使用

如果你没有make命令，可以直接使用docker-compose：

```bash
# 构建镜像
docker-compose build

# 运行Boids模拟
docker-compose run --rm boids

# 启动开发容器
docker-compose up -d bio-sim-dev

# 进入开发容器
docker-compose exec bio-sim-dev /bin/bash

# 运行测试
docker-compose run --rm bio-sim-test

# 停止所有容器
docker-compose down
```

---

## 显示图形界面（重要！）

### Windows
```bash
# 需要安装VcXsrv或Xming
# 设置DISPLAY环境变量在docker-compose.yml中
```

### Mac
```bash
# 安装XQuartz
brew install xquartz

# 启动XQuartz
open -a XQuartz

# 允许网络连接
# XQuartz -> Settings -> Security -> 勾选"Allow connections from network clients"

# 设置DISPLAY
export DISPLAY=host.docker.internal:0
```

### Linux
```bash
# 通常直接可用
export DISPLAY=:0
```

---

## 无界面模式（CI/CD）

对于测试和CI/CD，不需要图形界面：

```bash
# 运行测试（不需要显示）
docker-compose run --rm bio-sim-test
```

---

## 故障排除

### 问题1: 无法显示窗口
**解决方案**: 确保X服务器正在运行并允许连接

### 问题2: 权限错误
**解决方案**:
```bash
# Linux/Mac
sudo docker-compose run --rm bio-sim-test
```

### 问题3: 端口冲突
**解决方案**: 修改docker-compose.yml中的端口映射

### 问题4: 容器无法启动
**解决方案**:
```bash
# 清理并重新构建
make clean
make rebuild
```

---

## 性能优化

### 使用Volume缓存
Docker配置已经优化，代码修改会实时同步到容器。

### 减小镜像大小
使用了`python:3.10-slim`基础镜像，体积更小。

### 并行构建
```bash
docker-compose build --parallel
```

---

## 生产环境部署

### 使用外部显示服务器
```bash
# docker-compose.yml
environment:
  - DISPLAY=your-display-server:0
```

### Web版本（未来）
计划添加Web界面，届时可以完全在浏览器中运行。

---

## 资源限制

如果需要限制资源使用，修改docker-compose.yml：

```yaml
services:
  bio-sim-dev:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## 快捷命令别名

在你的 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
# Bio-Sim 快捷命令
alias bio-up='cd ~/bio_sim && make up'
alias bio-shell='cd ~/bio_sim && make shell'
alias bio-test='cd ~/bio_sim && make test'
alias bio-boids='cd ~/bio_sim && make boids'
```

---

**现在开始使用Docker享受零依赖的开发体验吧！** 🐳
