# Explorer Agent - 信息茧房突破智能体

一个能够自主探索、积累知识的AI智能体，帮助你发现信息茧房之外的内容。

## 功能特点

- **混合探索模式**：结合兴趣边缘扩展 + 随机探索 + 知识图谱连接
- **多数据源**：Google搜索、HackerNews、Arxiv、PubMed
- **智能评估**：自动判断内容价值，只保留有意义的发现
- **知识图谱**：建立内容之间的关联，记录探索路径
- **7x24运行**：后台持续探索，不断积累
- **可视化界面**：Streamlit仪表板查看探索结果

## 快速开始

### 1. 环境准备

```bash
# 安装 Docker Desktop (Windows)
# 下载：https://www.docker.com/products/docker-desktop/

# 或安装 Python 3.10+ 和 PostgreSQL 16
```

### 2. 配置环境变量

```bash
cd explorer-agent/backend
cp .env.example .env

# 编辑 .env 文件，填入 API Keys
# 必需：ANTHROPIC_API_KEY 或 OPENAI_API_KEY
```

### 3. 启动服务

```bash
# 使用 Docker (推荐)
docker-compose up -d

# 等待服务启动后，访问：
# - API文档：http://localhost:8000/docs
# - Streamlit界面：http://localhost:8501
```

### 4. 初始化数据库

```bash
docker-compose exec backend alembic upgrade head
```

## 目录结构

```
explorer-agent/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   ├── core/              # 核心配置
│   │   ├── db/                # 数据库会话
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   └── tasks/             # Celery 任务
│   ├── alembic/               # 数据库迁移
│   └── requirements.txt
├── frontend/                   # Streamlit 前端
│   └── app.py
└── docker-compose.yml
```

## 使用说明

### 手动触发探索

```bash
curl -X POST http://localhost:8000/api/v1/explore/start
```

### 查看探索结果

访问 http://localhost:8501 查看：
- 最新发现的内容
- 探索路径可视化
- 知识图谱
- 统计信息

### 调整探索策略

编辑 `backend/app/services/explorer.py` 中的参数：
- `EXPLORATION_INTERVAL_MINUTES`: 探索间隔
- `MAX_EXPLORATIONS_PER_RUN`: 每次运行的最大探索次数
- `MIN_VALUE_SCORE`: 最小价值分数阈值

## 技术栈

- **后端**: FastAPI + SQLAlchemy + Celery
- **数据库**: PostgreSQL + pgvector
- **缓存**: Redis
- **AI**: Anthropic Claude / OpenAI GPT
- **前端**: Streamlit
- **部署**: Docker

## 下一步开发

- [ ] 添加更多数据源（Twitter、Reddit等）
- [ ] 实现更智能的推荐算法
- [ ] 添加用户自定义兴趣标签
- [ ] 导出探索报告（Markdown/PDF）
- [ ] 多用户支持和权限管理

## License

MIT
