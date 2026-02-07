#!/bin/bash
# Explorer Agent 启动脚本 (Linux/Mac)

set -e

echo "============================================"
echo "  Explorer Agent - 启动脚本"
echo "============================================"
echo ""

# 检查 Docker
if ! docker info > /dev/null 2>&1; then
    echo "[错误] Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查 .env 文件
if [ ! -f "backend/.env" ]; then
    echo "[警告] 未找到 backend/.env 文件"
    echo "从 .env.example 创建 .env..."
    cp backend/.env.example backend/.env
    echo ""
    echo "[重要] 请编辑 backend/.env 并填入你的 API Keys:"
    echo "  - SILICONFLOW_API_KEY (推荐 - 硅基流动 DeepSeek)"
    echo "  - 或者 ANTHROPIC_API_KEY (Claude)"
    echo "  - 或者 OPENAI_API_KEY (GPT)"
    echo ""
    read -p "按 Enter 继续..."
fi

# 构建并启动
echo "[1/4] 构建并启动服务..."
docker-compose up -d --build

echo ""
echo "[2/4] 等待数据库启动..."
sleep 5

echo "[3/4] 初始化数据库..."
docker-compose exec -T backend python -c "from app.db.init_db import init_db; init_db()" || echo "[警告] 数据库初始化失败"

echo ""
echo "============================================"
echo "  启动完成！"
echo "============================================"
echo ""
echo "访问地址:"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - Streamlit 界面: http://localhost:8501"
echo "  - 后端日志: docker-compose logs -f backend"
echo "  - Worker 日志: docker-compose logs -f celery_worker"
echo ""
echo "常用命令:"
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "  - 触发探索: 访问 http://localhost:8501 点击'立即探索'"
echo ""
