#!/bin/bash
# 测试脚本 - 在Docker中运行测试

echo "🧪 Bio-Sim 测试套件"
echo "===================="

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

echo "✅ Docker运行正常"
echo ""

# 构建镜像（如果需要）
echo "📦 检查镜像..."
if ! docker image inspect bio-sim-bio-sim-dev > /dev/null 2>&1; then
    echo "构建镜像..."
    docker-compose build bio-sim-test
else
    echo "镜像已存在"
fi

echo ""
echo "🚀 运行测试..."
echo "===================="
docker-compose run --rm bio-sim-test

echo ""
echo "✅ 测试完成！"
echo ""
echo "查看覆盖率报告："
echo "  - 终端: 见上方输出"
echo "  - HTML: bio_sim/htmlcov/index.html"
