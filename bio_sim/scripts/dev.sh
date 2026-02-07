#!/bin/bash
# 开发环境启动脚本

echo "🐳 Bio-Sim 开发环境"
echo "===================="

# 检查Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 构建镜像
echo "📦 构建开发镜像..."
docker-compose build bio-sim-dev

# 启动开发容器
echo "🚀 启动开发容器..."
docker-compose up -d bio-sim-dev

echo ""
echo "✅ 开发环境已启动！"
echo ""
echo "可用命令："
echo "  make shell     - 进入容器"
echo "  make test      - 运行测试"
echo "  make format    - 格式化代码"
echo "  make lint      - 代码检查"
echo "  make down      - 停止容器"
echo ""
echo "进入容器："
echo "  docker-compose exec bio-sim-dev /bin/bash"
