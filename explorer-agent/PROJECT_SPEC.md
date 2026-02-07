# Explorer Agent - 项目规范

## 📋 项目概述

**项目名称**: Explorer Agent - 探索者-思考者智能体系统
**目标**: 突破信息茧房，深度挖掘低质量内容中的价值
**核心架构**: 探索者-思考者双AGENT模式
**技术栈**: Python + PostgreSQL + (可选)FastAPI + (可选)Streamlit

**架构原则**:
- **AGENT优先**: 核心逻辑可独立运行，不依赖Web框架
- **混合模式**: 既可作为Python包导入，也可通过API调用
- **依赖注入**: 所有组件可配置、可替换
- **前端最小化**: 前端仅作监控，核心功能无需GUI

---

## 🏗️ 项目架构

### 架构设计理念

```
核心设计: 探索者-思考者双AGENT模式

┌─────────────┐         ┌─────────────┐
│  Explorer   │────────▶│  Evaluator  │
│  (快速探索)  │         │  (快速筛选)  │
└─────────────┘         └──────┬───────┘
                               │
                   ┌───────────┴───────────┐
                   ▼                       ▼
           ┌───────────────┐       ┌──────────────┐
           │ 高质量内容     │       │ 低质量内容    │
           │ (直接保存)     │       │ (暂存池)     │
           └───────────────┘       └──────┬───────┘
                                           │
                                           ▼
                                    ┌───────────────┐
                                    │   Thinker     │
                                    │ (深度挖掘)     │
                                    └───────┬───────┘
                                            │
                            ┌───────────────┼─────────┐
                            ▼               ▼         ▼
                        ┌──────────┐  ┌─────────┐ ┌──────────┐
                        │ 隐藏宝石  │  │ 综合洞察 │ │ 发现关联 │
                        └──────────┘  └─────────┘ └──────────┘
```

### 目录结构（重构中）
```
explorer-agent/
├── backend/
│   ├── app/
│   │   ├── agents/              # ⭐ AGENT核心层
│   │   │   ├── base.py          # AgentProtocol接口
│   │   │   ├── explorer.py      # ExplorerAgent
│   │   │   ├── thinker.py       # ThinkerAgent
│   │   │   └── evaluator.py     # EvaluatorAgent
│   │   ├── services/            # 服务层（数据源、存储、AI）
│   │   ├── models/              # 数据模型
│   │   ├── db/                  # 数据库
│   │   ├── api/                 # API层（可选）
│   │   │   └── v1/              # HTTP端点
│   │   └── core/                # 配置
│   ├── scripts/                 # ⭐ 独立运行脚本
│   │   ├── run_exploration.py  # 直接调用Explorer
│   │   ├── run_thinking.py     # 直接调用Thinker
│   │   └── run_full_cycle.py   # 完整流程
│   └── tests/                   # 测试
├── frontend/                    # ⭐ 可选的监控界面
│   └── app.py                   # Streamlit（仅监控）
├── docs/                        # 文档
│   ├── ARCHITECTURE.md          # 架构设计文档
│   ├── AGENT_API.md             # AGENT调用API
│   └── RPD.md                   # 产品需求文档
├── docker-compose.yml           # Docker编排
└── README.md
```

### 运行模式

**模式1: 独立AGENT模式（推荐）**
```python
# 作为Python包直接使用
from app.agents.explorer import ExplorerAgent
from app.agents.thinker import ThinkerAgent

explorer = ExplorerAgent(config)
result = explorer.run({"query": "machine learning"})
```

**模式2: API服务模式（可选）**
```bash
# 通过HTTP API调用
curl -X POST http://localhost:8000/api/v1/agents/explorer/run \
  -d '{"query": "machine learning"}'
```

**模式3: 完全自动化模式**
```bash
# 通过Celery定时任务
python scripts/run_full_cycle.py
```

---

## 📝 开发规范

### 1. 代码风格
- 遵循 PEP 8 规范
- 使用类型注解
- 函数添加文档字符串
- 变量命名: snake_case
- 类命名: PascalCase

### 2. 提交规范
```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具链
```

### 3. 分支管理
- `main`: 主分支，稳定版本
- `dev`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支

---

## 🔄 工作流程

### 开发流程
1. 创建功能分支: `git checkout -b feature/xxx`
2. 编写代码 + 测试
3. 运行: `docker-compose up -d`
4. 测试功能
5. 提交: `git commit -m "feat: xxx"`
6. 推送: `git push origin feature/xxx`
7. 合并到 `dev`

### 调试流程
1. 查看日志: `docker-compose logs -f backend`
2. 查看Celery: `docker-compose logs -f celery_worker`
3. 进入容器: `docker-compose exec backend bash`
4. 测试API: `curl http://localhost:8000/api/v1/health`

---

## 🎯 当前任务清单

### 已完成 ✅
- [x] 项目架构搭建
- [x] 数据库模型设计
- [x] Arxiv论文搜索
- [x] AI评估系统集成（智谱AI GLM-4-Flash）
- [x] 前端界面（Streamlit）
- [x] Celery异步任务
- [x] Docker部署

### 进行中 🔄
- [ ] 完善测试覆盖
- [ ] 优化探索策略
- [ ] 添加更多数据源

### 待办 📋
- [ ] 单元测试
- [ ] API文档
- [ ] 性能优化
- [ ] 监控告警
- [ ] 用户手册

---

## 📊 当前状态

### 系统配置
- **AI评估器**: 智谱AI GLM-4-Flash (免费)
- **数据源**: Arxiv论文搜索
- **评分阈值**: 0.1 (低于此分不保存)
- **最大迭代**: 5次

### 数据统计
- **节点数**: 查看 http://localhost:8501
- **路径数**: 同上
- **种子数**: 同上

---

## 🚀 快速开始

### 启动系统
```bash
cd explorer-agent
docker-compose up -d
```

### 访问界面
- 前端: http://localhost:8501
- API文档: http://localhost:8000/docs

### 运行测试
```bash
python comprehensive_evaluation.py
```

---

## 📚 相关文档

### API端点
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/stats` - 统计信息
- `GET /api/v1/nodes` - 获取节点
- `POST /api/v1/explore/start` - 开始探索
- `POST /api/v1/frontier/add` - 添加种子

### 数据模型
- **Node**: 发现的内容节点
  - id, title, content, source, type, value_score, tags
- **Frontier**: 待探索种子
  - id, seed, priority, attempts, source_node_id
- **ExplorationPath**: 探索路径
  - id, path, strategy, total_value

---

## ⚠️ 常见问题

### Q: 探索没有创建节点？
A: 检查：
1. 日志: `docker-compose logs celery_worker`
2. AI评估是否正常
3. 内容是否已存在

### Q: 如何修改AI模型？
A: 编辑 `.env` 文件，修改API配置

### Q: 如何添加新数据源？
A: 在 `app/services/sources/` 创建新类

---

## 📞 联系方式

- 项目路径: `C:\Users\lenovo\explorer-agent`
- 日志位置: Docker容器日志
- 配置文件: `backend/.env`

---

**最后更新**: 2025-12-27
**版本**: 0.1.0
