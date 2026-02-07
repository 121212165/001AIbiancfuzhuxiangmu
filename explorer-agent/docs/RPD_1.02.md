# Explorer Agent - 产品需求文档 (RPD) v1.02

**文档版本**: 1.02
**创建日期**: 2025-12-29
**产品经理**: AI Product Manager
**项目状态**: 重构优化阶段
**上次更新**: 2025-12-29

---

## 文档修订历史

| 版本 | 日期 | 修订人 | 主要变更 |
|------|------|--------|----------|
| 1.02 | 2025-12-29 | Product Manager | 架构重构：AGENT优先、前端最小化、混合架构 |
| 1.01 | 2025-12-27 | Product Manager | 初始版本，基础功能定义 |

---

## 1. 产品概述

### 1.1 产品定位

**Explorer Agent** 是一个探索者-思考者双AGENT智能体系统，旨在突破信息茧房，从海量信息中自动发现、评估和挖掘有价值的内容。

**核心价值主张**:
- **深度挖掘**: 不止于表面探索，通过双AGENT模式深入挖掘低质量内容中的隐藏价值
- **智能评估**: AI驱动的内容价值评估，自动过滤噪音，保留精华
- **架构灵活**: AGENT优先设计，可作为Python包直接使用，也可通过API调用
- **前端最小化**: 前端仅作监控工具，核心功能无需GUI

### 1.2 产品愿景

成为最可靠的知识发现自动化平台，帮助研究者和开发者从信息过载中解放，专注于价值创造。

### 1.3 核心设计理念

```
┌────────────────────────────────────────────────────────────┐
│                    核心理念：AGENT优先                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 核心逻辑必须可独立运行 (不依赖FastAPI/HTTP)             │
│  2. 所有依赖必须可注入 (不硬编码)                            │
│  3. 支持混合运行模式 (独立/HTTP/Celery)                     │
│  4. 前端是可选工具 (不是必需品)                              │
│  5. AGENT间通过统一接口通信 (AgentProtocol)                 │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 2. 目标用户

### 2.1 主要用户画像

**用户1: 研究人员**
- **痛点**: 信息过载，难以从海量文献中发现有价值的研究方向
- **需求**: 自动筛选高质量论文，发现跨领域关联
- **使用场景**: 每周运行一次，获取领域前沿动态

**用户2: 技术探索者**
- **痛点**: 容易陷入技术栈的信息茧房，错过新技术趋势
- **需求**: 发现意想不到但有价值的内容
- **使用场景**: 作为Python包集成到自己的工具链

**用户3: 内容创作者**
- **痛点**: 需要持续挖掘灵感和素材
- **需求**: 从多个数据源发现创意，洞察趋势
- **使用场景**: 通过API集成到内容管理系统

### 2.2 用户使用模式

| 模式 | 适用用户 | 接口方式 | 典型场景 |
|------|----------|----------|----------|
| 独立AGENT | 开发者、研究者 | 直接import Python包 | 集成到自定义脚本 |
| HTTP API | 非技术人员 | REST API | 通过Web界面调用 |
| Celery任务 | 自动化场景 | 定时任务 | 7x24小时自动探索 |
| 前端监控 | 所有用户 | Streamlit界面 | 查看运行状态和结果 |

---

## 3. 核心功能 (v1.02版本)

### 3.1 功能优先级矩阵

```
高业务价值 ─────────────────────────────────────
  │
  │  [P0] ExplorerAgent      [P1] ThinkerAgent
  │  探索与快速筛选          深度挖掘与洞察
  │
  │  [P0] EvaluatorAgent     [P2] 前端监控界面
  │  AI价值评估              (最小化)
  │
  │  [P1] 依赖注入重构       [P2] HTTP API包装
  │  架构优化                (可选)
  │
  └────────────────────────────────────────────▶
低开发成本                        高开发成本

P0 = 必须完成 (MVP)
P1 = 应该完成 (重要)
P2 = 可以完成 (可选)
```

### 3.2 ExplorerAgent - 探索者 (P0)

**功能描述**: 从多种数据源发现内容，评估内容价值，按质量分级处理

**核心职责**:
1. **内容发现**: 从Arxiv、Web等数据源搜索内容
2. **快速评估**: 调用EvaluatorAgent进行价值评分
3. **分级处理**:
   - 高质量内容 (score >= 0.3): 直接保存到数据库
   - 低质量内容 (score < 0.3): 放入暂存池，等待ThinkerAgent处理

**输入参数**:
```python
{
    "query": "machine learning",  # 搜索关键词
    "max_results": 10,            # 最大结果数
    "sources": ["arxiv", "web"]   # 数据源列表
}
```

**输出结果**:
```python
{
    "status": "success",          # 执行状态
    "high_quality": [...],        # 高质量内容列表
    "low_quality": [...],         # 低质量内容列表
    "metrics": {
        "total_discovered": 10,
        "high_quality_count": 3,
        "low_quality_count": 7,
        "execution_time": 5.2
    }
}
```

**验收标准**:
- AC1: 支持至少2个数据源 (Arxiv, Web)
- AC2: 可以直接import使用，不依赖FastAPI
- AC3: 所有依赖通过构造函数注入
- AC4: 执行时间 < 30秒 (单次探索)

### 3.3 ThinkerAgent - 思考者 (P1)

**功能描述**: 从低质量池中提取内容，深度分析挖掘隐藏价值

**核心职责**:
1. **挖掘宝石**: 从被过滤的内容中发现潜在价值
2. **综合洞察**: 跨内容关联分析，生成高层次洞察
3. **发现关联**: 识别内容间的隐藏联系

**工作模式**:
- `mine_gems`: 从低质量内容中挖掘被低估的宝石
- `synthesize`: 综合多篇内容生成洞察
- `discover_connections`: 发现内容间的隐藏关联
- `auto`: 自动选择最佳模式

**输入参数**:
```python
{
    "items": [...],              # 低质量内容列表
    "mode": "auto"               # 工作模式
}
```

**输出结果**:
```python
{
    "status": "success",
    "insights": [...],           # 洞察列表
    "connections": [...],        # 关联列表
    "gems_found": 2,             # 发现的宝石数量
    "metrics": {...}
}
```

**验收标准**:
- AC1: 支持3种工作模式
- AC2: 可以独立运行，或处理ExplorerAgent的输出
- AC3: 依赖通过构造函数注入
- AC4: 生成可解释的洞察结果

### 3.4 EvaluatorAgent - 评估器 (P0)

**功能描述**: AI驱动的内容价值评估，提供一致的评分标准

**核心职责**:
1. **多维评估**: 新颖性、质量、潜力三个维度
2. **提供商管理**: 支持多个AI提供商，自动降级
3. **标签提取**: 自动提取内容标签

**评估标准**:
```python
{
    "novelty": 0.8,      # 新颖性 (0-1)
    "quality": 0.7,      # 质量 (0-1)
    "potential": 0.6,    # 潜力 (0-1)
    "final_score": 0.7,  # 最终得分 (加权平均)
    "reasoning": "...",  # 评分理由
    "tags": ["AI", "ML"] # 提取的标签
}
```

**AI提供商优先级**:
1. 智谱AI GLM-4-Flash (主要，免费)
2. 硅基流动 DeepSeek V3 (备用)
3. 火山引擎 豆包 (备用)
4. 通义千问 Qwen (备用)
5. OpenRouter免费模型 (最后备用)

**验收标准**:
- AC1: 支持至少3个AI提供商
- AC2: API失败时自动降级，降级时间 < 1秒
- AC3: 评分一致性 (相同内容评分差异 < 0.2)
- AC4: 单次评估响应 < 5秒

### 3.5 前端监控界面 (P2)

**功能定位**: 前端不是必需品，是可选的监控工具

**包含功能**:
- 实时监控AGENT运行状态
- 查看数据库统计信息
- 浏览探索结果
- 手动触发探索 (可选)

**不包含功能** (核心功能在后端):
- 核心业务逻辑
- AGENT编排
- 系统配置 (使用配置文件)

**验收标准**:
- AC1: 仅展示和监控，不包含核心逻辑
- AC2: 可以完全移除前端，系统仍可正常运行
- AC3: 界面简洁，加载时间 < 3秒

---

## 4. 技术架构

### 4.1 架构原则 (必须遵守)

基于 `ARCHITECTURE.md` 的架构要求：

#### 4.1.1 AGENT优先原则

**核心逻辑必须可独立运行**:
```python
# 正确示例: AGENT可以独立使用
from app.agents.explorer import ExplorerAgent
from app.agents.evaluator import EvaluatorAgent

evaluator = EvaluatorAgent(provider="zhipuai")
explorer = ExplorerAgent(
    sources=[ArxivSource()],
    evaluator=evaluator,
    storage=PostgresStorage()
)

result = explorer.run({"query": "machine learning"})
# 无需FastAPI、无需HTTP、无需Celery
```

**禁止示例**:
```python
# 错误示例: AGENT依赖FastAPI
class ExplorerAgent:
    def __init__(self):
        self.db = Depends(get_db)  # ❌ 依赖FastAPI
        self.http_client = httpx.Client()  # ❌ 硬编码依赖
```

#### 4.1.2 混合架构支持

系统必须支持3种运行模式：

**模式1: 作为Python包直接import使用**
```python
# 推荐用于AGENT间协作
from explorer_agents import ExplorerAgent, ThinkerAgent

explorer = ExplorerAgent(config)
thinker = ThinkerAgent(config)

# 直接调用
result = explorer.run(...)
insights = thinker.run(...)
```

**模式2: 通过HTTP API调用 (可选)**
```python
# FastAPI只是AGENT的HTTP包装
import requests
response = requests.post(
    "http://localhost:8000/api/v1/agents/explorer/run",
    json={"query": "machine learning"}
)
```

**模式3: 通过Celery定时任务 (可选)**
```python
# Celery仅用于异步调度
@celery_app.task
def scheduled_exploration():
    explorer = ExplorerAgent(config)
    return explorer.run(...)
```

#### 4.1.3 依赖注入

**所有AGENT的依赖必须可配置**:
```python
# 正确示例: 依赖注入
class ExplorerAgent:
    def __init__(self,
                 sources: List[DataSource],
                 evaluator: EvaluatorAgent,
                 storage: Storage):
        self.sources = sources      # ✅ 注入
        self.evaluator = evaluator  # ✅ 注入
        self.storage = storage      # ✅ 注入

# 错误示例: 硬编码依赖
class ExplorerAgent:
    def __init__(self):
        self.sources = [ArxivSource()]        # ❌ 硬编码
        self.evaluator = EvaluatorAgent()     # ❌ 硬编码
        self.storage = PostgresStorage(...)   # ❌ 硬编码
```

#### 4.1.4 前端定位

**前端职责范围**:

| 功能 | 是否应该在前端 | 说明 |
|------|----------------|------|
| 实时监控AGENT状态 | ✅ | 前端更直观 |
| 查看探索结果 | ✅ | 可视化展示 |
| 浏览数据库统计 | ✅ | 图表展示 |
| 手动触发探索 | ⚠️ | 可选，脚本更好 |
| AGENT编排 | ❌ | 在Orchestrator层 |
| 核心业务逻辑 | ❌ | 在AGENT层 |
| 系统配置管理 | ❌ | 使用配置文件 |

### 4.2 AGENT接口规范

所有AGENT必须实现统一的 `AgentProtocol` 接口：

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

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

### 4.3 AGENT间调用规范

**推荐方式: 直接同步调用**
```python
# ExplorerAgent调用EvaluatorAgent
class ExplorerAgent:
    def __init__(self, evaluator: EvaluatorAgent):
        self.evaluator = evaluator

    def run(self, input_data):
        items = self.sources[0].discover(input_data["query"])

        for item in items:
            # 直接同步调用，无需HTTP
            score = self.evaluator.evaluate(item)

            if score >= 0.3:
                self.storage.save(item)
```

**禁止方式: AGENT间通过HTTP调用**
```python
# ❌ 错误示例
class ExplorerAgent:
    def run(self, input_data):
        # 不要通过HTTP调用其他AGENT
        response = requests.post(
            "http://localhost:8000/api/v1/agents/evaluator/run",
            json={"item": item}
        )
```

### 4.4 目录结构 (v1.02重构后)

```
explorer-agent/
├── backend/
│   ├── app/
│   │   ├── agents/              # ⭐ AGENT核心层
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # AgentProtocol接口
│   │   │   ├── explorer.py      # ExplorerAgent实现
│   │   │   ├── thinker.py       # ThinkerAgent实现
│   │   │   ├── evaluator.py     # EvaluatorAgent实现
│   │   │   └── orchestrator.py  # 多AGENT编排 (可选)
│   │   ├── services/            # 服务层
│   │   │   ├── sources/         # 数据源实现
│   │   │   │   ├── base.py      # DataSource接口
│   │   │   │   ├── arxiv.py     # Arxiv数据源
│   │   │   │   └── web.py       # Web数据源
│   │   │   ├── storage/         # 存储实现
│   │   │   │   ├── base.py      # Storage接口
│   │   │   │   └── database.py  # 数据库存储
│   │   │   └── ai/              # AI provider实现
│   │   │       ├── base.py      # AIProvider接口
│   │   │       └── zhipuai.py   # 智谱AI实现
│   │   ├── models/              # 数据模型
│   │   ├── db/                  # 数据库会话
│   │   ├── api/                 # ⭐ API层 (可选)
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           └── agents.py  # AGENT的HTTP包装
│   │   ├── main.py              # FastAPI入口 (可选)
│   │   └── core/
│   │       └── config.py        # 配置管理
│   ├── scripts/                 # ⭐ 独立运行脚本
│   │   ├── run_exploration.py  # 直接运行Explorer
│   │   ├── run_thinking.py     # 直接运行Thinker
│   │   └── run_full_cycle.py   # 完整流程
│   └── tests/                   # 测试
├── frontend/                    # ⭐ 前端 (最小化)
│   └── app.py                   # Streamlit监控界面
├── docs/                        # ⭐ 文档
│   ├── ARCHITECTURE.md          # 架构设计文档
│   ├── AGENT_API.md             # AGENT调用API文档
│   ├── RPD_1.02.md              # 本文档
│   └── examples/                # 使用示例
│       ├── standalone_agent.py  # 独立AGENT示例
│       └── api_service.py       # API服务示例
├── docker-compose.yml
└── README.md
```

---

## 5. 技术债务与重构计划

### 5.1 当前技术债务

**债务1: 前端比例过大**
- **问题**: 前端承担了过多职责
- **影响**: 违反"前端最小化"原则
- **优先级**: P1

**债务2: 硬编码依赖**
- **问题**: AGENT内部硬编码依赖，难以测试和替换
- **影响**: 违反"依赖注入"原则
- **优先级**: P0

**债务3: 缺少AGENT统一接口**
- **问题**: AGENT间调用不规范
- **影响**: 代码耦合度高，难以维护
- **优先级**: P0

**债务4: FastAPI与AGENT逻辑耦合**
- **问题**: AGENT依赖FastAPI的Depends
- **影响**: 无法独立运行AGENT
- **优先级**: P0

### 5.2 重构路线图

#### Phase 1: 接口抽象 (Week 1-2)
**目标**: 建立AGENT统一接口

**任务**:
- [ ] 定义 `AgentProtocol` 接口
- [ ] 定义 `DataSource` 接口
- [ ] 定义 `Storage` 接口
- [ ] 定义 `AIProvider` 接口
- [ ] 编写接口使用示例

**验收标准**:
- 所有接口定义完成
- 接口文档完善
- 单元测试覆盖率 > 80%

#### Phase 2: AGENT重构 (Week 3-4)
**目标**: 重构现有AGENT实现统一接口

**任务**:
- [ ] 重构 `ExplorerAgent`
  - 移除硬编码依赖
  - 实现依赖注入
  - 符合AgentProtocol
- [ ] 重构 `EvaluatorAgent`
  - 抽离AI provider
  - 实现依赖注入
  - 符合AgentProtocol
- [ ] 重构 `ThinkerAgent`
  - 实现依赖注入
  - 符合AgentProtocol

**验收标准**:
- 所有AGENT实现AgentProtocol
- 可以直接import使用，不依赖FastAPI
- 依赖通过构造函数注入

#### Phase 3: API层重构 (Week 5)
**目标**: API层变为AGENT的HTTP包装

**任务**:
- [ ] 移除FastAPI端的业务逻辑
- [ ] API端点仅调用AGENT.run()
- [ ] 统一错误处理
- [ ] API文档更新

**验收标准**:
- API层代码量 < 200行
- API不包含业务逻辑
- 移除API后系统仍可运行

#### Phase 4: 前端最小化 (Week 6)
**目标**: 精简前端功能

**任务**:
- [ ] 移除前端的核心业务逻辑
- [ ] 前端仅保留监控功能
- [ ] 添加独立脚本替代前端功能
- [ ] 更新前端文档

**验收标准**:
- 前端代码量减少50%
- 可以完全移除前端
- CLI工具功能完整

#### Phase 5: 文档与示例 (Week 7)
**目标**: 完善文档和使用示例

**任务**:
- [ ] 编写 `AGENT_API.md`
- [ ] 编写独立运行示例
- [ ] 编写API服务示例
- [ ] 更新README
- [ ] 编写迁移指南

**验收标准**:
- 文档覆盖率100%
- 示例代码可运行
- 用户可以5分钟内上手

---

## 6. 前端策略

### 6.1 前端最小化原则

**核心理念**: 前端不是必需品，是可选的监控工具

```
┌────────────────────────────────────────────────────────────┐
│                   前端功能定位                             │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  应该做的 (监控和展示):                                     │
│  - 实时监控AGENT运行状态                                     │
│  - 查看数据库统计信息                                        │
│  - 浏览探索结果列表                                          │
│  - 查看日志和错误                                            │
│                                                             │
│  不应该做的 (核心功能在后端):                                │
│  - AGENT编排逻辑 ❌                                         │
│  - 核心业务逻辑 ❌                                          │
│  - 系统配置管理 ❌ (用配置文件)                              │
│  - 批量任务调度 ❌ (用Celery/脚本)                          │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 6.2 前端vs后端职责划分

| 功能模块 | 前端职责 | 后端职责 | 推荐方式 |
|---------|---------|---------|---------|
| 触发探索 | 提供按钮 | 执行逻辑 | 脚本更好 |
| 查看结果 | 可视化展示 | 数据提供 | 前端展示 |
| 系统配置 | ❌ 不推荐 | 读取配置文件 | 配置文件 |
| AGENT编排 | ❌ 不支持 | Orchestrator | 直接调用 |
| 日志查看 | 界面展示 | 文件/数据库 | 各有优势 |

### 6.3 前端功能清单 (v1.02)

**保留功能**:
1. **实时监控面板**
   - AGENT运行状态
   - 数据库统计 (节点数、路径数)
   - 系统健康检查

2. **结果浏览器**
   - 高质量内容列表
   - 洞察展示
   - 质量分析图表

3. **日志查看器**
   - 实时日志流
   - 错误日志过滤
   - 性能指标

**移除功能**:
1. ❌ 复杂配置管理 (改用配置文件)
2. ❌ AGENT编排逻辑 (移到Orchestrator)
3. ❌ 批量操作 (改用脚本)

### 6.4 CLI工具替代方案

对于前端移除的功能，提供CLI工具替代：

```bash
# 触发探索
python scripts/run_exploration.py --query "machine learning"

# 查看统计
python scripts/show_stats.py

# 查看结果
python scripts/show_results.py --limit 10

# 完整流程
python scripts/run_full_cycle.py
```

---

## 7. 里程碑与交付计划

### 7.1 版本规划

```
v1.02 (重构版) ────────────────────────────────────────┐
│                                                         │
│  Phase 1: 接口抽象        (Week 1-2)                    │
│  ├─ AgentProtocol接口定义                               │
│  ├─ DataSource/Storage/AIProvider接口                   │
│  └─ 单元测试                                             │
│                                                         │
│  Phase 2: AGENT重构       (Week 3-4)                    │
│  ├─ ExplorerAgent重构                                  │
│  ├─ EvaluatorAgent重构                                 │
│  └─ ThinkerAgent重构                                   │
│                                                         │
│  Phase 3: API层重构      (Week 5)                       │
│  ├─ FastAPI变为HTTP包装                                 │
│  └─ 统一错误处理                                         │
│                                                         │
│  Phase 4: 前端最小化     (Week 6)                       │
│  ├─ 移除前端核心逻辑                                     │
│  └─ 添加CLI工具                                         │
│                                                         │
│  Phase 5: 文档完善       (Week 7)                       │
│  ├─ AGENT API文档                                        │
│  ├─ 使用示例                                             │
│  └─ 迁移指南                                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 7.2 交付里程碑

**Milestone 1: 接口抽象完成 (Week 2)**
- 交付物:
  - `app/agents/base.py` - AgentProtocol接口
  - `app/services/sources/base.py` - DataSource接口
  - `app/services/storage/base.py` - Storage接口
  - `app/services/ai/base.py` - AIProvider接口
  - 接口文档
- 验收标准:
  - 所有接口定义完成
  - 接口文档完善
  - 单元测试通过

**Milestone 2: AGENT重构完成 (Week 4)**
- 交付物:
  - 重构后的 `ExplorerAgent`
  - 重构后的 `EvaluatorAgent`
  - 重构后的 `ThinkerAgent`
  - 单元测试和集成测试
- 验收标准:
  - 所有AGENT符合AgentProtocol
  - 可以直接import使用
  - 依赖通过构造函数注入
  - 测试覆盖率 > 80%

**Milestone 3: API层重构完成 (Week 5)**
- 交付物:
  - 重构后的FastAPI端点
  - API文档
- 验收标准:
  - API层代码量 < 200行
  - API不包含业务逻辑
  - 移除API后系统仍可运行

**Milestone 4: 前端最小化完成 (Week 6)**
- 交付物:
  - 精简后的前端界面
  - CLI工具集
- 验收标准:
  - 前端代码量减少50%
  - 可以完全移除前端
  - CLI工具功能完整

**Milestone 5: v1.02版本发布 (Week 7)**
- 交付物:
  - 完整文档 (AGENT_API.md, README更新)
  - 使用示例 (standalone_agent.py, api_service.py)
  - 迁移指南
  - Docker镜像
- 验收标准:
  - 文档覆盖率100%
  - 示例代码可运行
  - 用户可以5分钟内上手
  - Docker部署成功

### 7.3 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 重构破坏现有功能 | 高 | 中 | 完整的单元测试和集成测试 |
| 依赖注入实现复杂 | 中 | 中 | 使用简单的DI容器 |
| API层重构引入Bug | 中 | 低 | 充分的API测试 |
| 前端功能缺失影响用户 | 低 | 低 | 提供CLI工具替代 |
| 文档不完善影响上手 | 中 | 中 | 优先编写文档 |

---

## 8. 成功指标

### 8.1 架构质量指标

**代码质量**:
- [ ] AGENT代码单元测试覆盖率 > 80%
- [ ] 所有AGENT符合AgentProtocol接口
- [ ] 零硬编码依赖
- [ ] API层代码量 < 200行
- [ ] 前端代码量减少50%

**架构一致性**:
- [ ] 所有AGENT可以独立运行 (不依赖FastAPI)
- [ ] 所有依赖通过构造函数注入
- [ ] 可以完全移除前端，系统正常运行
- [ ] 可以完全移除API层，系统正常运行

**文档完整性**:
- [ ] 接口文档覆盖率 100%
- [ ] 使用示例可运行
- [ ] 迁移指南完善

### 8.2 功能指标

**ExplorerAgent (P0)**:
- [ ] 支持至少2个数据源 (Arxiv, Web)
- [ ] 单次探索耗时 < 30秒
- [ ] 高质量内容识别准确率 > 70% (基于用户反馈)

**EvaluatorAgent (P0)**:
- [ ] 支持至少3个AI提供商
- [ ] API失败时自动降级时间 < 1秒
- [ ] 单次评估响应 < 5秒
- [ ] 评估成功率 > 95% (包括降级)

**ThinkerAgent (P1)**:
- [ ] 支持3种工作模式
- [ ] 可以处理ExplorerAgent的输出
- [ ] 生成可解释的洞察结果

### 8.3 用户体验指标

**上手时间**:
- [ ] 新用户5分钟内可以运行第一个示例
- [ ] 30分钟内可以集成到自己的项目

**使用便捷性**:
- [ ] 提供至少3个使用示例
- [ ] CLI工具功能完整
- [ ] 前端监控界面加载时间 < 3秒

### 8.4 业务价值指标

**系统性能**:
- [ ] 单次完整探索周期 < 60秒
- [ ] 系统可用性 > 99%

**内容价值**:
- [ ] 高质量内容发现率 > 30%
- [ ] 低质量内容中挖掘宝石率 > 10%
- [ ] 用户满意度 > 80% (基于反馈)

---

## 9. 非功能性需求

### 9.1 性能要求

| 指标 | 要求 | 测量方式 |
|------|------|----------|
| AGENT启动时间 | < 2秒 | 单元测试 |
| 单次探索耗时 | < 30秒 | 集成测试 |
| 单次评估耗时 | < 5秒 | 单元测试 |
| API响应时间 | < 1秒 | API测试 |
| 前端加载时间 | < 3秒 | 性能测试 |

### 9.2 可靠性要求

| 指标 | 要求 | 测量方式 |
|------|------|----------|
| API失败降级时间 | < 1秒 | 集成测试 |
| 系统可用性 | > 99% | 监控统计 |
| 数据持久化保证 | 100% | 数据库测试 |
| 错误日志完整性 | 100% | 日志审计 |

### 9.3 可维护性要求

| 指标 | 要求 | 测量方式 |
|------|------|----------|
| 代码测试覆盖率 | > 80% | 测试报告 |
| 接口文档覆盖率 | 100% | 文档审计 |
| 代码规范符合率 | 100% | Linter检查 |
| 依赖注入覆盖率 | 100% | 代码审查 |

### 9.4 可扩展性要求

| 指标 | 要求 | 测量方式 |
|------|------|----------|
| 新增AGENT工作量 | < 1天 | 开发统计 |
| 新增数据源工作量 | < 0.5天 | 开发统计 |
| 新增AI提供商工作量 | < 0.5天 | 开发统计 |
| 系统支持1000+节点 | 是 | 压力测试 |

---

## 10. 约束与假设

### 10.1 技术约束

- **C1**: 免费AI API可能有速率限制
- **C2**: 不同AI模型的评分标准可能不同
- **C3**: PostgreSQL + pgvector必须在v1.02中支持
- **C4**: Docker部署必须在v1.02中支持

### 10.2 资源约束

- **R1**: 开发周期：7周
- **R2**: 开发人力：1-2人
- **R3**: AI API成本：优先使用免费API

### 10.3 假设

- **A1**: 用户对Python有基础了解
- **A2**: AI评估结果基本可靠 (平均误差 < 0.2)
- **A3**: 用户理解前端是可选工具
- **A4**: Docker环境可用

---

## 11. 附录

### 11.1 术语表

| 术语 | 定义 |
|------|------|
| AGENT | 具有自主决策能力的智能体模块 |
| ExplorerAgent | 探索者AGENT，负责内容发现和快速筛选 |
| ThinkerAgent | 思考者AGENT，负责深度挖掘和洞察生成 |
| EvaluatorAgent | 评估器AGENT，负责AI驱动的内容价值评估 |
| AgentProtocol | AGENT统一接口协议 |
| 依赖注入 | 通过构造函数传入依赖，而非内部创建 |
| 混合架构 | 支持独立运行、API调用、定时任务三种模式 |
| 前端最小化 | 前端仅作监控，核心功能无需GUI |

### 11.2 参考文档

- `ARCHITECTURE.md` - 架构设计文档
- `PROJECT_SPEC.md` - 项目规范
- `specs/exploration-engine/requirements.md` - 探索引擎需求
- `specs/ai-evaluator/requirements.md` - AI评估器需求
- `specs/web-ui/requirements.md` - Web界面需求

### 11.3 变更请求流程

1. 提交变更请求到Issue
2. Product Manager评估影响
3. 更新RPD文档
4. 通知开发团队
5. 更新测试用例

---

## 12. 审批与签署

| 角色 | 姓名 | 签名 | 日期 |
|------|------|------|------|
| Product Manager | AI Product Manager | | 2025-12-29 |
| Tech Lead | | | |
| Engineering Lead | | | |

---

**文档状态**: ✅ 已发布

**下次评审**: 根据开发进度，每周五评审一次

**联系方式**: 如有问题或建议，请提交Issue或联系Product Manager

---

**版本历史**:
- v1.02 (2025-12-29) - 架构重构版本，强调AGENT优先、前端最小化
- v1.01 (2025-12-27) - 初始版本，基础功能定义
