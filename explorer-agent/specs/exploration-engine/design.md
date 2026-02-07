# Design - Exploration Engine (探索引擎)

## Architecture Overview

### System Architecture
```
┌─────────────────────────────────────────────┐
│          Frontend (Streamlit)                │
│  - 用户界面                                    │
│  - 控制面板                                    │
│  - 数据展示                                    │
└──────────────────┬──────────────────────────┘
                   │ HTTP API
┌──────────────────▼──────────────────────────┐
│          Backend (FastAPI)                   │
│  - REST API                                   │
│  - 任务调度                                    │
│  - 数据管理                                    │
└──────────────────┬──────────────────────────┘
                   │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌───▼────┐   ┌───▼────────┐
│  PostgreSQL│  │Redis  │   │Celery Worker│
│  (数据存储)│  │(任务队列)│ │(异步探索)    │
└───────────┘  └────────┘   └──────────────┘
                            │
                    ┌───────▼────────┐
                    │ ExplorationEngine│
                    │  - Arxiv搜索     │
                    │  - AI评估        │
                    │  - 路径记录      │
                    └──────────────────┘
```

### Component Design

#### 1. ExplorationEngine (探索引擎)
**职责**: 协调整个探索流程

**核心方法**:
```python
class ExplorationEngine:
    def explore(strategy, max_iterations) -> Dict:
        """执行探索
        Args:
            strategy: 探索策略 (random/edge/graph/mixed)
            max_iterations: 最大迭代次数
        Returns:
           探索结果 (nodes_created, paths_created)
        """

    def _explore_from_seed(seed, strategy) -> Dict:
        """从种子探索"""

    def _add_seeds_from_discovery(node, discovery):
        """从发现内容生成新种子"""
```

**探索策略**:
- `random`: 随机选择种子
- `edge`: 优先选择边缘种子（有来源节点的）
- `graph`: 图遍历，选择高价值路径
- `mixed`: 混合策略

#### 2. ValueEvaluator (AI评估器)
**职责**: 评估内容价值

**支持AI提供商**:
1. 智谱AI GLM-4-Flash (免费) ← 当前使用
2. 硅基流动 DeepSeek V3 (付费)
3. 火山引擎 豆包 (付费)
4. 通义千问 Qwen (付费)
5. OpenRouter 免费模型

**评估逻辑**:
```python
def evaluate(content, existing_nodes) -> float:
    # 1. 构建上下文
    context = _build_context(existing_nodes)

    # 2. 调用AI
    response = ai_client.chat.completions.create(
        model=glm_4_flash,
        messages=[{
            "role": "user",
            "content": f"评估内容价值(0-1): {content[:2000]}"
        }]
    )

    # 3. 解析评分
    score = float(response.choices[0].message.content)

    # 4. 返回
    return max(0.0, min(1.0, score))
```

#### 3. DataSource (数据源接口)
**职责**: 统一数据源接口

**接口设计**:
```python
class DataSource(ABC):
    @abstractmethod
    def search(query: str, num_results: int) -> List[Dict]:
        """搜索内容
        Returns:
            标准化结果: {
                "title": str,
                "content": str,
                "source": str,  # URL
                "type": str     # paper/article/post
            }
        """
```

**已实现数据源**:
- ArxivSource: 学术论文
- DuckDuckGoSource: 通用搜索
- RedditSource: 社区讨论
- HackerNewsSource: 技术新闻
- GitHubTrendingSource: 开源项目
- StackOverflowSource: 技术问答
- PubMedSource: 医学研究

### Data Model

#### Node (节点)
```python
class Node(Base):
    id: Integer              # 主键
    title: String(500)       # 标题
    content: Text            # 内容摘要
    source: String(500)      # 来源URL
    type: String(50)         # 类型
    value_score: Float       # AI评分
    tags: JSON               # 标签数组
    discovered_at: DateTime  # 发现时间
    meta_data: Text          # 额外数据
```

#### Frontier (探索边界)
```python
class Frontier(Base):
    id: Integer
    seed: String(500)        # 种子文本
    priority: Float          # 优先级 (0-1)
    attempts: Integer        # 尝试次数
    source_node_id: Integer  # 来源节点ID
    last_attempt_at: DateTime
```

#### ExplorationPath (探索路径)
```python
class ExplorationPath(Base):
    id: Integer
    path: JSON              # 节点ID数组
    strategy: String(50)     # 策略
    total_value: Float       # 路径总价值
    started_at: DateTime
    completed_at: DateTime
```

### Technology Stack

**Backend**:
- FastAPI: Web框架
- SQLAlchemy: ORM
- PostgreSQL: 数据库 + pgvector扩展
- Redis: 缓存和消息队列
- Celery: 异步任务

**Frontend**:
- Streamlit: 快速Web UI
- Plotly: 数据可视化
- Pandas: 数据处理

**AI Services**:
- OpenAI SDK: API统一接口
- 智谱AI GLM-4-Flash: 主要评估器
- 硅基流动: 备用评估器

### Deployment

**Docker Compose**:
```yaml
services:
  backend:
    image: explorer-agent-backend
    ports: ["8000:8000"]

  frontend:
    image: explorer-agent-frontend
    ports: ["8501:8501"]

  postgres:
    image: pgvector/pgvector:pg16

  redis:
    image: redis:7-alpine

  celery_worker:
    image: explorer-agent-backend
    command: celery worker
```

### Algorithm Design

#### 种子选择算法
```python
def _get_next_seed(strategy):
    frontier = db.query(Frontier)

    if strategy == "random":
        return frontier.order_by(func.random()).first()

    elif strategy == "edge":
        return frontier.filter(
            Frontier.source_node_id.isnot(None)
        ).order_by(Frontier.priority.desc()).first()

    elif strategy == "graph":
        # 选择高价值路径的种子
        high_value_paths = db.query(ExplorationPath).filter(
            ExplorationPath.total_value > 1.0
        )
        # ... 复杂逻辑

    else:  # mixed
        return frontier.order_by(
            Frontier.priority.desc()
        ).first()
```

#### 新种子生成算法
```python
def _add_seeds_from_discovery(node, discovery):
    """从发现内容生成新种子"""
    # 1. 提取关键词
    words = extract_keywords(discovery['content'])

    # 2. 过滤常见词
    keywords = filter_common_words(words)

    # 3. 选择top关键词
    top_keywords = keywords[:10]

    # 4. 生成种子
    for kw in top_keywords:
        seed_text = f"{kw} research"

        # 检查是否已存在
        if not db.query(Frontier).filter_by(seed=seed_text).first():
            db.add(Frontier(
                seed=seed_text,
                priority=random.uniform(0.3, 0.8),
                source_node_id=node.id
            ))
```

### Risks & Mitigations

**风险1**: AI API不稳定
- **缓解**: 多提供商备份，自动降级

**风险2**: Arxiv速率限制
- **缓解**: 添加延迟，使用缓存

**风险3**: 内容重复
- **缓解**: URL去重检查

**风险4**: 评分主观性
- **缓解**: 多模型交叉验证

### Performance Optimization

**优化1**: 批量AI评估
```python
# 当前: 逐个评估
for content in contents:
    score = evaluator.evaluate(content)

# 优化: 批量评估
scores = evaluator.evaluate_batch(contents)
```

**优化2**: 异步搜索
```python
# 使用 asyncio 并行搜索多个数据源
async def search_multiple_sources(query):
    tasks = [source.search(query) for source in sources]
    results = await asyncio.gather(*tasks)
```

**优化3**: 缓存热门查询
```python
@lru_cache(maxsize=100)
def cached_search(query):
    return arxiv.search(query)
```

---

**设计完成时间**: 2025-12-27
**设计师**: Claude Code
**版本**: 1.0
