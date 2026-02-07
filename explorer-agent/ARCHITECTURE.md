# Explorer Agent - 架构设计文档

**版本**: 1.0
**最后更新**: 2025-12-29
**架构类型**: 混合架构（独立AGENT + API服务）

---

## 📐 架构原则

### 核心设计理念

本系统采用**混合架构设计**，支持两种运行模式：

1. **独立AGENT模式**：作为Python包直接导入使用
2. **API服务模式**：通过HTTP API提供服务

```
┌─────────────────────────────────────────────────────────────┐
│                    混合架构设计原则                        │
├─────────────────────────────────────────────────────────────┤
│ 1. AGENT优先：核心逻辑不依赖FastAPI/HTTP                   │
│ 2. 接口解耦：AGENT通过抽象接口通信，不直接依赖实现          │
│ 3. 依赖注入：所有组件可替换、可配置                         │
│ 4. 双模式运行：既可以独立运行，也可以作为服务暴露          │
│ 5. 前端最小化：前端仅作监控，核心功能无需GUI               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ 系统架构

### 架构层次

```
┌────────────────────────────────────────────────────────────┐
│                      应用层                                │
├──────────────────────┬─────────────────────────────────────┤
│   独立AGENT模式       │           API服务模式                │
│                      │                                      │
│  from explorer_agents │  HTTP Client                       │
│  import ExplorerAgent │      ↓                             │
│                      │  FastAPI Endpoints                 │
│  explorer = Explorer- │      ↓                             │
│    Agent(config)      │  AGENT Layer (复用同一逻辑)        │
│  explorer.run()       │                                      │
└──────────────────────┴─────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                   AGENT层 (核心)                           │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐      │
│  │ ExplorerAgent│  │ ThinkerAgent│  │ EvaluatorAgent│     │
│  ├─────────────┤  ├─────────────┤  ├──────────────┤      │
│  │ - discover() │  │ - mine_gems()│ │ - evaluate()  │      │
│  │ - explore()  │  │ - synthesize()│ │ - extract_tags()│  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                           ↓                                 │
│                 ┌──────────────────┐                        │
│                 │  AgentProtocol   │                        │
│                 │  (ABC Interface) │                        │
│                 └──────────────────┘                        │
└────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────┐
│                   服务层 (可选)                            │
├────────────────────────────────────────────────────────────┤
│  DataSource    │    AIProvider    │    Storage              │
│  - ArxivSource │    - OpenAI      │    - Database           │
│  - WebSource   │    - Anthropic   │    - VectorStore        │
│                │    - ZhipuAI     │                          │
└────────────────────────────────────────────────────────────┘
```

---

## 🎯 核心组件设计

### 1. AGENT接口抽象

所有AGENT必须实现统一的接口协议：

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class AgentProtocol(ABC):
    """AGENT统一接口协议"""

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行AGENT核心逻辑

        Args:
            input_data: 输入数据

        Returns:
            Dict包含:
                - status: "success" | "partial" | "failed"
                - data: 处理结果
                - metrics: 性能指标
                - errors: 错误列表（如有）
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict) -> bool:
        """验证输入数据"""
        pass

    def get_config(self) -> Dict:
        """获取当前配置"""
        return self._config
```

### 2. 依赖注入容器

```python
class DIContainer:
    """简单的依赖注入容器"""

    def __init__(self):
        self._services = {}
        self._factories = {}

    def register(self, name: str, instance: Any):
        """注册服务实例"""
        self._services[name] = instance

    def register_factory(self, name: str, factory: callable):
        """注册工厂函数"""
        self._factories[name] = factory

    def get(self, name: str) -> Any:
        """获取服务"""
        if name in self._services:
            return self._services[name]
        if name in self._factories:
            return self._factories[name]()
        raise ValueError(f"Service {name} not found")
```

### 3. ExplorerAgent设计

```python
class ExplorerAgent(AgentProtocol):
    """
    探索者AGENT

    职责：
    1. 从多种数据源发现内容
    2. 评估内容价值
    3. 高价值内容保存到数据库
    4. 低价值内容放入暂存池
    """

    def __init__(self,
                 sources: List[DataSource],  # 注入数据源
                 evaluator: EvaluatorAgent,  # 注入评估器
                 storage: Storage):         # 注入存储
        """
        通过依赖注入初始化，不硬编码任何依赖
        """
        self.sources = sources
        self.evaluator = evaluator
        self.storage = storage
        self.config = {}

    def run(self, input_data: Dict) -> Dict:
        """
        执行探索

        支持同步调用，不依赖Celery/HTTP
        """
        results = {
            "status": "success",
            "high_quality": [],
            "low_quality": [],
            "metrics": {}
        }

        for source in self.sources:
            items = source.discover(input_data["query"])

            for item in items:
                score = self.evaluator.evaluate(item)

                if score >= self.config.get("min_score", 0.3):
                    results["high_quality"].append(item)
                    self.storage.save(item)
                else:
                    results["low_quality"].append(item)
                    self.storage.save_to_pool(item)

        return results
```

### 4. ThinkerAgent设计

```python
class ThinkerAgent(AgentProtocol):
    """
    思考者AGENT

    职责：
    1. 从低质量池提取内容
    2. 深度分析挖掘价值
    3. 生成洞察
    4. 发现关联
    """

    def __init__(self,
                 ai_provider: AIAgent,
                 storage: Storage):
        self.ai = ai_provider
        self.storage = storage

    def run(self, input_data: Dict) -> Dict:
        """
        执行思考

        可以直接处理Explorer的输出
        """
        mode = input_data.get("mode", "auto")
        items = input_data["items"]

        if mode == "mine_gems":
            return self._mine_gems(items)
        elif mode == "synthesize":
            return self._synthesize(items)
        elif mode == "discover_connections":
            return self._discover_connections(items)
        else:
            return self._auto_mode(items)
```

---

## 🔄 调用模式

### 模式1: 独立AGENT调用（推荐用于AGENT间协作）

```python
# 直接导入，同步调用
from app.agents.explorer import ExplorerAgent
from app.agents.thinker import ThinkerAgent
from app.agents.evaluator import EvaluatorAgent
from app.services.sources import ArxivSource
from app.db.storage import PostgresStorage

# 配置依赖
storage = PostgresStorage(db_url="...")
evaluator = EvaluatorAgent(provider="zhipuai")
sources = [ArxivSource()]

# 创建AGENT
explorer = ExplorerAgent(
    sources=sources,
    evaluator=evaluator,
    storage=storage
)

# 同步调用，直接返回结果
result = explorer.run({
    "query": "machine learning",
    "max_results": 10
})

# Thinker处理低质量内容
thinker = ThinkerAgent(ai_provider=evaluator, storage=storage)
insights = thinker.run({
    "items": result["low_quality"],
    "mode": "auto"
})

# 完成整个流程，无需HTTP、无需Celery
```

### 模式2: API服务调用（用于Web界面/远程调用）

```python
# 通过HTTP API调用
import requests

# 探索
response = requests.post(
    "http://localhost:8000/api/v1/agents/explorer/run",
    json={
        "query": "machine learning",
        "max_results": 10
    }
)
result = response.json()

# 思考
response = requests.post(
    "http://localhost:8000/api/v1/agents/thinker/run",
    json={
        "items": result["low_quality"],
        "mode": "auto"
    }
)
insights = response.json()
```

---

## 📂 目录结构（重构后）

```
explorer-agent/
├── backend/
│   ├── app/
│   │   ├── agents/              # ⭐ AGENT核心层
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # AgentProtocol接口
│   │   │   ├── explorer.py      # ExplorerAgent
│   │   │   ├── thinker.py       # ThinkerAgent
│   │   │   ├── evaluator.py     # EvaluatorAgent
│   │   │   └── orchestrator.py  # Orchestrator（编排多AGENT）
│   │   ├── services/            # 服务层
│   │   │   ├── sources/         # 数据源实现
│   │   │   ├── storage/         # 存储实现
│   │   │   └── ai/              # AI provider实现
│   │   ├── models/              # 数据模型
│   │   ├── db/                  # 数据库
│   │   ├── api/                 # ⭐ API层（可选）
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   └── agents.py  # AGENT的HTTP包装
│   │   │       └── __init__.py
│   │   ├── main.py              # FastAPI入口（可选）
│   │   └── core/
│   │       └── config.py
│   ├── scripts/                 # ⭐ 独立脚本
│   │   ├── run_exploration.py  # 直接运行Explorer
│   │   ├── run_thinking.py     # 直接运行Thinker
│   │   └── run_full_cycle.py   # 完整流程
│   └── tests/                   # 测试
├── frontend/                    # ⭐ 前端（最小化，仅监控）
│   └── app.py                   # Streamlit监控界面
├── docs/                        # ⭐ 文档
│   ├── ARCHITECTURE.md          # 本文档
│   ├── AGENT_API.md             # AGENT调用API文档
│   └── HTTP_API.md              # HTTP API文档（可选）
└── examples/                    # ⭐ 使用示例
    ├── standalone_agent.py      # 独立AGENT示例
    └── api_service.py           # API服务示例
```

---

## 🎨 前端定位

### 前端最小化原则

**前端不是必需品，而是可选的监控工具。**

| 功能 | 前端 | CLI/脚本 | 说明 |
|------|------|----------|------|
| 查看统计 | ✅ 可视化 | ✅ 命令行 | 前端更直观 |
| 触发探索 | ✅ 按钮 | ✅ 脚本 | 脚本更适合自动化 |
| 查看日志 | ✅ 界面 | ✅ 文件 | 各有优势 |
| 系统配置 | ❌ 不推荐 | ✅ 配置文件 | 配置文件更可靠 |
| AGENT调用 | ❌ 无此功能 | ✅ 直接import | 核心功能无需前端 |

### 前端职责范围

```python
# 前端应该做的事情（仅监控和展示）

1. 实时监控
   - AGENT运行状态
   - 数据库统计
   - 系统健康检查

2. 结果查看
   - 探索结果列表
   - 洞察展示
   - 质量分析图表

3. 手动操作（可选）
   - 添加种子
   - 触发单次探索
   - 查看日志

# 前端不应该做的事情

❌ 核心业务逻辑（在AGENT层）
❌ AGENT编排（在Orchestrator层）
❌ 复杂配置管理（用配置文件）
❌ 批量任务调度（用脚本/Celery）
```

---

## 🔧 实现路线图

### Phase 1: 接口抽象（优先级：高）
- [ ] 定义AgentProtocol接口
- [ ] 重构ExplorerAgent
- [ ] 重构ThinkerAgent
- [ ] 重构EvaluatorAgent

### Phase 2: 依赖注入（优先级：高）
- [ ] 实现DIContainer
- [ ] 移除硬编码依赖
- [ ] 配置外部化

### Phase 3: API层重构（优先级：中）
- [ ] FastAPI变为AGENT的HTTP包装
- [ ] API层不再包含业务逻辑
- [ ] 统一错误处理

### Phase 4: 前端最小化（优先级：中）
- [ ] 移除前端的核心逻辑
- [ ] 前端仅保留监控功能
- [ ] 添加CLI工具

### Phase 5: 文档和示例（优先级：中）
- [ ] AGENT调用文档
- [ ] 独立运行示例
- [ ] API服务示例

---

## 📚 设计模式

### 1. 策略模式 - 数据源
```python
class DataSource(ABC):
    @abstractmethod
    def discover(self, query: str) -> List[Item]:
        pass

class ArxivSource(DataSource): ...
class WebSource(DataSource): ...
```

### 2. 依赖注入 - AGENT初始化
```python
# 不推荐
class ExplorerAgent:
    def __init__(self):
        self.evaluator = ValueEvaluator()  # 硬编码

# 推荐
class ExplorerAgent:
    def __init__(self, evaluator: EvaluatorAgent):  # 注入
        self.evaluator = evaluator
```

### 3. 工厂模式 - AGENT创建
```python
class AgentFactory:
    @staticmethod
    def create_explorer(config: Dict) -> ExplorerAgent:
        return ExplorerAgent(
            sources=config["sources"],
            evaluator=config["evaluator"],
            storage=config["storage"]
        )
```

### 4. 编排器模式 - 多AGENT协作
```python
class Orchestrator:
    def run_full_cycle(self):
        explorer_result = self.explorer.run(...)
        thinker_result = self.thinker.run({
            "items": explorer_result["low_quality"]
        })
        return {
            "exploration": explorer_result,
            "insights": thinker_result
        }
```

---

## 🔒 关键约束

### 必须遵守

1. **AGENT不能依赖FastAPI**
   - AGENT必须可以独立运行
   - FastAPI只是可选的HTTP包装

2. **AGENT不能依赖Celery**
   - Celery仅用于异步任务调度
   - AGENT核心逻辑必须同步可调用

3. **所有依赖必须可注入**
   - 不允许硬编码依赖
   - 通过构造函数注入

4. **配置外部化**
   - 配置从环境变量或配置文件读取
   - 不在代码中硬编码配置

### 可以灵活处理

1. **数据持久化方式**
   - 可以是数据库、文件、内存
   - 通过Storage接口抽象

2. **AI提供商**
   - 可以是OpenAI、Anthropic、本地模型
   - 通过AIProvider接口抽象

3. **前端实现**
   - Streamlit、React、或无前端
   - 前端不影响核心逻辑

---

## 📊 性能考虑

### 同步 vs 异步

| 场景 | 推荐方式 | 原因 |
|------|---------|------|
| AGENT间调用 | 同步函数调用 | 简单、高效、易调试 |
| Web API请求 | 异步(Celery) | 避免阻塞 |
| 长时间任务 | 异步(Celery) | 避免超时 |
| 批量处理 | 异步(Celery) | 并行处理 |

```
AGENT核心逻辑 → 同步（简单可靠）
     ↓
如果需要异步 → 用Celery包装（不改变核心逻辑）
     ↓
如果需要HTTP → 用FastAPI包装（不改变核心逻辑）
```

---

## 🧪 测试策略

### 单元测试

```python
# AGENT测试不需要启动FastAPI/Celery
def test_explorer_agent():
    # 使用Mock依赖
    mock_source = Mock(spec=DataSource)
    mock_evaluator = Mock(spec=EvaluatorAgent)
    mock_storage = Mock(spec=Storage)

    # 直接测试AGENT逻辑
    explorer = ExplorerAgent(
        sources=[mock_source],
        evaluator=mock_evaluator,
        storage=mock_storage
    )

    result = explorer.run({"query": "test"})

    assert result["status"] == "success"
```

### 集成测试

```python
def test_full_cycle():
    # 真实依赖，测试AGENT协作
    explorer = ExplorerAgent(...)
    thinker = ThinkerAgent(...)

    explore_result = explorer.run(...)
    think_result = thinker.run({
        "items": explore_result["low_quality"]
    })

    assert len(think_result["insights"]) > 0
```

---

## 📖 相关文档

- `AGENT_API.md` - AGENT编程接口文档
- `HTTP_API.md` - HTTP API文档（可选）
- `PROJECT_SPEC.md` - 项目规范
- `README.md` - 快速开始

---

**文档维护**: 本文档随架构演进同步更新
**版本历史**:
- 1.0 (2025-12-29) - 初始版本，定义混合架构
