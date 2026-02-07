# Explorer Agent - 快速开始指南

## 📋 前置要求

1. **Docker Desktop** (Windows) 或 **Docker** (Linux/Mac)
   - 下载：https://www.docker.com/products/docker-desktop/

2. **硅基流动 API Key** (推荐)
   - 注册：https://cloud.siliconflow.cn/
   - 新用户可得 2000万 Tokens
   - 创建 API Key：登录后访问 https://cloud.siliconflow.cn/account/ak

## 🚀 快速启动

### Windows 用户

1. 双击运行 `start.bat`
2. 等待服务启动完成
3. 访问 http://localhost:8501

### Linux/Mac 用户

1. 给予执行权限：`chmod +x start.sh`
2. 运行：`./start.sh`
3. 访问 http://localhost:8501

## ⚙️ 配置说明

编辑 `backend/.env` 文件：

```bash
# 必需配置（选择一个即可）
SILICONFLOW_API_KEY=sk-your-key-here  # 推荐：硅基流动 DeepSeek
# 或者
# ANTHROPIC_API_KEY=sk-ant-your-key-here  # Claude
# 或者
# OPENAI_API_KEY=sk-your-key-here  # GPT

# 数据库（默认配置即可）
DATABASE_URL=postgresql://explorer:password@localhost:5432/explorer_db

# Redis（默认配置即可）
REDIS_URL=redis://localhost:6379/0

# 探索参数
EXPLORATION_INTERVAL_MINUTES=30   # 探索间隔（分钟）
MAX_EXPLORATIONS_PER_RUN=5        # 每次最大探索次数
MIN_VALUE_SCORE=0.3               # 最小价值分数阈值
```

## 📖 使用说明

### 1. 查看界面

访问 http://localhost:8501，你会看到：
- **控制面板**：左侧边栏
- **最新发现**：最近探索的内容
- **探索路径**：A→B→C 的发现链条
- **价值分数分布**：直方图统计

### 2. 触发探索

点击左侧的 **"🚀 立即探索"** 按钮开始探索。

### 3. 查看结果

- 探索过程会自动运行，发现有价值的内容
- 价值分数 > 0.7 的内容会显示 ⭐ 标记
- 点击展开可以查看详细内容和标签

### 4. API 调用

也可以通过 API 触发探索：

```bash
# 手动触发探索
curl -X POST http://localhost:8000/api/v1/explore/start

# 查看统计信息
curl http://localhost:8000/api/v1/stats

# 查看发现的节点
curl http://localhost:8000/api/v1/nodes

# 查看探索路径
curl http://localhost:8000/api/v1/paths

# 添加自定义探索种子
curl -X POST "http://localhost:8000/api/v1/frontier/add?seed=blockchain%20research&priority=1.0"
```

## 🔍 硅基流动 API 调用说明

硅基流动的 API 兼容 OpenAI 格式，非常简单：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_siliconflow_api_key",
    base_url="https://api.siliconflow.cn/v1"
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3",
    messages=[{"role": "user", "content": "你好"}],
    max_tokens=100
)

print(response.choices[0].message.content)
```

**支持的模型：**
- `deepseek-ai/DeepSeek-V3` (最新)
- `deepseek-ai/DeepSeek-R1`
- `Qwen/Qwen2.5-72B-Instruct`
- 更多模型见：https://docs.siliconflow.cn/

## 🛠️ 常见问题

### Q: Docker 启动失败？

A: 确保 Docker Desktop 正在运行。Windows 用户可能需要启用 WSL 2。

### Q: 探索没有发现内容？

A: 检查：
1. API Key 是否正确配置
2. 查看日志：`docker-compose logs -f backend`
3. 可能需要调整 `MIN_VALUE_SCORE` 阈值

### Q: 如何停止服务？

A:
```bash
docker-compose down  # 停止并删除容器
docker-compose down -v  # 停止并删除数据卷（清空数据库）
```

### Q: 数据库在哪里？

A: 数据存储在 Docker volume 中。如果需要备份：
```bash
docker exec explorer-agent-postgres-1 pg_dump -U explorer explorer_db > backup.sql
```

### Q: 如何自定义探索策略？

A: 编辑 `backend/app/services/explorer.py`，修改：
- `_add_random_seeds()`: 初始种子
- `_explore_from_seed()`: 数据源选择逻辑
- `MIN_VALUE_SCORE`: 价值阈值

## 📊 项目结构

```
explorer-agent/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API 路由（待扩展）
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库会话
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── evaluator.py       # 价值评估器
│   │   │   ├── explorer.py        # 探索引擎
│   │   │   └── sources/           # 数据源
│   │   └── tasks/          # Celery 任务
│   ├── alembic/            # 数据库迁移
│   ├── requirements.txt
│   └── .env                # 配置文件（重要！）
├── frontend/               # Streamlit 前端
│   └── app.py
├── docker-compose.yml
├── start.bat              # Windows 启动脚本
└── start.sh               # Linux/Mac 启动脚本
```

## 🎯 下一步

- [ ] 添加更多数据源（Twitter、Reddit）
- [ ] 实现更智能的推荐算法
- [ ] 添加用户自定义兴趣标签
- [ ] 导出探索报告（Markdown/PDF）
- [ ] 实现知识图谱可视化

## 📝 License

MIT

## 🙋 获取帮助

遇到问题？
1. 查看 [README.md](README.md)
2. 检查日志：`docker-compose logs -f`
3. 查看 API 文档：http://localhost:8000/docs

---

**Sources:**
- [硅基流动 API 调用](https://zhuanlan.zhihu.com/p/18966056589)
- [2025最新 DeepSeek API 使用指南](https://www.cursor-ide.com/blog/deepseek-r1-api-guide)
- [硅基流动 API 文档](https://www.explinks.com/blog/ua-silicon-based-flow-api-call-examples-and-application-guide/)
- [硅基流动官网](https://siliconflow.cn/)
