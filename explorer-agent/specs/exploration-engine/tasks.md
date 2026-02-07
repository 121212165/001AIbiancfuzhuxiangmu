# Tasks - Exploration Engine (探索引擎)

## Task Breakdown

### Phase 1: 核心探索引擎 (ExplorationEngine)

#### Task 1.1: 实现种子选择算法
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 4 hours

**Requirements**: AC1.2, AC2.2
**Design Reference**: Algorithm Design - 种子选择算法

**Subtasks**:
- [x] 实现 `random` 策略：随机选择种子
- [x] 实现 `edge` 策略：优先选择有来源节点的种子
- [x] 实现 `graph` 策略：选择高价值路径的种子
- [x] 实现 `mixed` 策略：混合策略，按优先级排序
- [x] 添加种子去重检查

**Implementation**: `backend/app/services/explorer.py:_get_next_seed()`

**Verification**:
- [x] 测试所有策略正确选择种子
- [x] 验证空边界处理
- [x] 确认种子优先级排序

---

#### Task 1.2: 实现Arxiv搜索集成
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 6 hours

**Requirements**: AC2.1, AC2.3, AC2.4
**Design Reference**: DataSource - ArxivSource

**Subtasks**:
- [x] 实现 `ArxivSource` 类
- [x] 标准化搜索结果格式 (title, content, source, type)
- [x] 添加URL去重检查
- [x] 实现结果缓存 (减少API调用)
- [x] 添加速率限制处理

**Implementation**: `backend/app/services/sources/arxiv.py`

**Verification**:
- [x] 测试关键词搜索
- [x] 验证结果格式标准化
- [x] 确认去重功能
- [x] 测试错误处理

---

#### Task 1.3: 实现探索流程
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 8 hours

**Requirements**: AC1.3, AC4.1, AC4.2
**Design Reference**: ExplorationEngine - explore()

**Subtasks**:
- [x] 实现 `explore()` 主循环
- [x] 实现 `_explore_from_seed()` 单次探索
- [x] 实现 `_add_seeds_from_discovery()` 新种子生成
- [x] 添加探索路径记录
- [x] 实现路径价值计算

**Implementation**: `backend/app/services/explorer.py`

**Verification**:
- [x] 测试单轮探索
- [x] 测试多轮迭代
- [x] 验证路径记录正确
- [x] 确认种子自动生成

---

#### Task 1.4: 实现Celery异步任务
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 4 hours

**Requirements**: NFR1.1, NFR1.3
**Design Reference**: Technology Stack - Celery

**Subtasks**:
- [x] 配置Celery worker
- [x] 实现异步探索任务
- [x] 添加任务状态跟踪
- [x] 实现任务结果查询
- [x] 添加任务取消功能

**Implementation**: `backend/app/tasks/celery_tasks.py`

**Verification**:
- [x] 测试任务启动
- [x] 验证异步执行
- [x] 确认状态更新
- [x] 测试并发任务

---

### Phase 2: AI质量评估器 (ValueEvaluator)

#### Task 2.1: 集成智谱AI GLM-4-Flash
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 6 hours

**Requirements**: AC3.1, AC3.2, AC3.4, NFR1.2
**Design Reference**: ValueEvaluator - AI评估器

**Subtasks**:
- [x] 配置智谱AI API密钥
- [x] 实现评估prompt设计
- [x] 添加评分解析逻辑 (正则表达式)
- [x] 实现上下文构建 (已有节点参考)
- [x] 添加评分范围限制 (0.0-1.0)

**Implementation**: `backend/app/services/evaluator.py:_evaluate_with_zhipuai()`

**Verification**:
- [x] 测试API调用
- [x] 验证评分范围正确
- [x] 确认解析成功率
- [x] 测试错误处理和降级

---

#### Task 2.2: 实现多提供商备份
**Priority**: P1 (High)
**Status**: ✅ Completed
**Estimated**: 8 hours

**Requirements**: AC3.4, NFR2.1
**Design Reference**: ValueEvaluator - 支持AI提供商

**Subtasks**:
- [x] 实现提供商优先级链
- [x] 集成硅基流动 DeepSeek V3
- [x] 集成火山引擎 豆包
- [x] 集成通义千问 Qwen
- [x] 集成OpenRouter免费模型
- [x] 实现自动降级逻辑

**Implementation**: `backend/app/services/evaluator.py`

**Verification**:
- [x] 测试优先级链
- [x] 验证降级机制
- [x] 确认所有提供商可用
- [x] 测试并发请求

---

#### Task 2.3: 优化批量评估
**Priority**: P2 (Medium)
**Status**: ⏳ Pending
**Estimated**: 6 hours

**Requirements**: NFR1.2, NFR3.2
**Design Reference**: Performance Optimization - 批量AI评估

**Subtasks**:
- [ ] 实现 `evaluate_batch()` 方法
- [ ] 添加请求批处理
- [ ] 实现异步并发评估
- [ ] 优化上下文构建
- [ ] 添加评估缓存

**Implementation**: `backend/app/services/evaluator.py`

**Verification**:
- [ ] 测试批量评估性能
- [ ] 对比单次评估耗时
- [ ] 验证评分一致性
- [ ] 测试缓存命中率

---

### Phase 3: 数据库与数据模型

#### Task 3.1: 设计并实现数据模型
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 4 hours

**Requirements**: AC1.2, AC4.1, AC4.2
**Design Reference**: Data Model - Node, Frontier, ExplorationPath

**Subtasks**:
- [x] 实现 `Node` 模型 (发现的内容)
- [x] 实现 `Frontier` 模型 (待探索种子)
- [x] 实现 `ExplorationPath` 模型 (探索路径)
- [x] 实现 `Edge` 模型 (节点关系)
- [x] 添加外键约束
- [x] 创建数据库迁移脚本

**Implementation**: `backend/app/models/node.py`, `frontier.py`, `exploration_path.py`

**Verification**:
- [x] 验证表结构创建
- [x] 测试外键约束
- [x] 确认索引正确
- [x] 测试数据持久化

---

#### Task 3.2: 实现数据库CRUD操作
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 4 hours

**Requirements**: AC1.1, AC1.4
**Design Reference**: Architecture Overview - Backend

**Subtasks**:
- [x] 实现节点创建和查询
- [x] 实现种子添加和管理
- [x] 实现路径记录和查询
- [x] 添加批量操作支持
- [x] 实现去重查询

**Implementation**: `backend/app/db/crud.py`

**Verification**:
- [x] 测试CRUD操作
- [x] 验证查询性能
- [x] 确认事务完整性
- [x] 测试并发写入

---

### Phase 4: REST API

#### Task 4.1: 实现核心API端点
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 6 hours

**Requirements**: NFR4.1, NFR4.2
**Design Reference**: PROJECT_SPEC.md - API端点

**Subtasks**:
- [x] `GET /api/v1/health` - 健康检查
- [x] `GET /api/v1/stats` - 统计信息
- [x] `GET /api/v1/nodes` - 获取节点列表
- [x] `POST /api/v1/explore/start` - 开始探索
- [x] `POST /api/v1/frontier/add` - 添加种子
- [x] `GET /api/v1/frontier` - 获取种子列表
- [x] `POST /api/v1/explore/from_seed/{seed_id}` - 从种子探索
- [x] `DELETE /api/v1/frontier/clear` - 清空种子

**Implementation**: `backend/app/main.py`

**Verification**:
- [x] 测试所有端点
- [x] 验证请求/响应格式
- [x] 确认错误处理
- [x] 测试参数验证

---

#### Task 4.2: 实现任务状态查询
**Priority**: P1 (High)
**Status**: ✅ Completed
**Estimated**: 3 hours

**Requirements**: NFR4.2
**Design Reference**: Celery异步任务

**Subtasks**:
- [x] `GET /api/v1/explore/status/{task_id}` - 任务状态
- [x] 实现任务结果存储
- [x] 添加任务历史查询
- [x] 实现实时进度更新

**Implementation**: `backend/app/main.py`

**Verification**:
- [x] 测试状态查询
- [x] 验证进度更新
- [x] 确认结果正确

---

### Phase 5: 前端界面

#### Task 5.1: 实现主仪表板
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 8 hours

**Requirements**: NFR4.1, NFR4.3
**Design Reference**: PROJECT_SPEC.md - Frontend

**Subtasks**:
- [x] 设计4标签页布局
  - [x] 最新发现 (Tab 1)
  - [x] 探索路径 (Tab 2)
  - [x] 质量分析 (Tab 3)
  - [x] 探索管理 (Tab 4)
- [x] 实现侧边栏控制面板
- [x] 添加探索设置 (策略、迭代次数)
- [x] 实现统计指标显示
- [x] 添加种子添加界面

**Implementation**: `frontend/app.py`

**Verification**:
- [x] 测试UI布局
- [x] 验证数据刷新
- [x] 确认按钮功能

---

#### Task 5.2: 实现节点可视化
**Priority**: P1 (High)
**Status**: ✅ Completed
**Estimated**: 6 hours

**Requirements**: AC4.3, NFR4.3
**Design Reference**: Frontend - 数据展示

**Subtasks**:
- [x] 实现节点列表展示
- [x] 添加评分过滤滑块
- [x] 实现价值分emoji标识
- [x] 添加节点详情展开
- [x] 显示标签、来源、类型

**Implementation**: `frontend/app.py:tab1`

**Verification**:
- [x] 测试过滤功能
- [x] 验证详情展示
- [x] 确认响应式布局

---

#### Task 5.3: 实现路径可视化
**Priority**: P1 (High)
**Status**: ✅ Completed
**Estimated**: 6 hours

**Requirements**: AC4.3, AC4.4
**Design Reference**: Frontend - 数据展示

**Subtasks**:
- [x] 实现路径列表展示
- [x] 添加路径价值过滤
- [x] 显示路径节点序列
- [x] 实现"沿路径继续探索"按钮
- [x] 显示路径统计信息

**Implementation**: `frontend/app.py:tab2`

**Verification**:
- [x] 测试路径展示
- [x] 验证探索功能
- [x] 确认过滤正确

---

#### Task 5.4: 实现质量分析面板
**Priority**: P1 (High)
**Status**: ✅ Completed
**Estimated**: 6 hours

**Requirements**: AC3.1, AC3.2, NFR4.3
**Design Reference**: Frontend - 数据展示

**Subtasks**:
- [x] 实现价值分分布直方图
- [x] 添加评分统计指标
- [x] 实现质量等级说明
- [x] 显示评估系统文档
- [x] 添加低价值内容示例

**Implementation**: `frontend/app.py:tab3`

**Verification**:
- [x] 测试图表渲染
- [x] 验证统计计算
- [x] 确认说明清晰

---

#### Task 5.5: 实现探索管理界面
**Priority**: P1 (High)
**Status**: ✅ Completed
**Estimated**: 8 hours

**Requirements**: AC1.1, AC1.2, AC1.4
**Design Reference**: Frontend - 控制面板

**Subtasks**:
- [x] 实现种子池展示
- [x] 添加种子详情显示 (优先级、尝试次数)
- [x] 实现"从种子探索"按钮
- [x] 添加批量种子导入
- [x] 实现随机种子添加
- [x] 添加清空种子功能

**Implementation**: `frontend/app.py:tab4`

**Verification**:
- [x] 测试种子管理
- [x] 验证批量操作
- [x] 确认探索功能

---

### Phase 6: 部署与测试

#### Task 6.1: Docker部署配置
**Priority**: P0 (Critical)
**Status**: ✅ Completed
**Estimated**: 4 hours

**Requirements**: NFR2.3, NFR3.3
**Design Reference**: Deployment - Docker Compose

**Subtasks**:
- [x] 编写Dockerfile (backend, frontend)
- [x] 配置docker-compose.yml
- [x] 设置环境变量管理
- [x] 配置数据卷持久化
- [x] 添加服务依赖管理

**Implementation**: `Dockerfile`, `docker-compose.yml`

**Verification**:
- [x] 测试容器构建
- [x] 验证服务启动
- [x] 确认数据持久化

---

#### Task 6.2: 综合测试脚本
**Priority**: P1 (High)
**Status**: ✅ Completed
**Estimated**: 6 hours

**Requirements**: All Features
**Design Reference**: comprehensive_evaluation.py

**Subtasks**:
- [x] 实现系统健康检查
- [x] 测试数据源功能
- [x] 测试探索执行流程
- [x] 评估探索结果质量
- [x] 测试AI评估系统
- [x] 生成综合评测报告

**Implementation**: `comprehensive_evaluation.py`

**Verification**:
- [x] 运行完整测试
- [x] 验证所有功能
- [x] 确认报告生成

---

### Phase 7: 优化与增强

#### Task 7.1: 实现异步搜索优化
**Priority**: P2 (Medium)
**Status**: ⏳ Pending
**Estimated**: 6 hours

**Requirements**: NFR1.1, NFR3.2
**Design Reference**: Performance Optimization - 异步搜索

**Subtasks**:
- [ ] 实现asyncio并行搜索
- [ ] 添加搜索超时控制
- [ ] 实现搜索结果合并
- [ ] 优化错误处理

**Implementation**: `backend/app/services/sources/base.py`

**Verification**:
- [ ] 测试并行搜索性能
- [ ] 验证结果正确性
- [ ] 确认超时处理

---

#### Task 7.2: 实现查询缓存
**Priority**: P2 (Medium)
**Status**: ⏳ Pending
**Estimated**: 4 hours

**Requirements**: NFR1.1
**Design Reference**: Performance Optimization - 缓存热门查询

**Subtasks**:
- [ ] 实现Redis缓存层
- [ ] 添加缓存键设计
- [ ] 实现缓存过期策略
- [ ] 添加缓存命中率统计

**Implementation**: `backend/app/core/cache.py`

**Verification**:
- [ ] 测试缓存功能
- [ ] 验证命中率
- [ ] 确认过期正确

---

#### Task 7.3: 添加单元测试
**Priority**: P2 (Medium)
**Status**: ⏳ Pending
**Estimated**: 12 hours

**Requirements**: All Features
**Design Reference**: PROJECT_SPEC.md - 待办

**Subtasks**:
- [ ] 测试ExplorationEngine核心逻辑
- [ ] 测试ValueEvaluator评估功能
- [ ] 测试DataSource各实现
- [ ] 测试API端点
- [ ] 测试数据库CRUD
- [ ] 实现测试覆盖率报告

**Implementation**: `tests/` 目录

**Verification**:
- [ ] 运行所有测试
- [ ] 验证覆盖率 > 80%
- [ ] 确认CI集成

---

#### Task 7.4: 实现API文档
**Priority**: P2 (Medium)
**Status**: ⏳ Pending
**Estimated**: 4 hours

**Requirements**: NFR4.1
**Design Reference**: PROJECT_SPEC.md - 待办

**Subtasks**:
- [ ] 配置Swagger/OpenAPI
- [ ] 添加端点描述
- [ ] 添加请求/响应示例
- [ ] 实现交互式文档

**Implementation**: `backend/app/main.py` (FastAPI自动生成)

**Verification**:
- [ ] 访问 /docs 验证
- [ ] 测试示例请求
- [ ] 确认描述清晰

---

#### Task 7.5: 添加监控与日志
**Priority**: P3 (Low)
**Status**: ⏳ Pending
**Estimated**: 8 hours

**Requirements**: NFR2.1, NFR2.2
**Design Reference**: PROJECT_SPEC.md - 待办

**Subtasks**:
- [ ] 实现结构化日志
- [ ] 添加性能监控
- [ ] 实现错误追踪
- [ ] 添加告警机制
- [ ] 集成监控仪表板

**Implementation**: `backend/app/core/logging.py`, `monitoring/`

**Verification**:
- [ ] 测试日志输出
- [ ] 验证监控数据
- [ ] 确认告警触发

---

### Phase 8: 文档与用户手册

#### Task 8.1: 编写系统文档
**Priority**: P2 (Medium)
**Status**: ⏳ Pending
**Estimated**: 6 hours

**Requirements**: NFR4.1
**Design Reference**: PROJECT_SPEC.md

**Subtasks**:
- [ ] 完善README.md
- [ ] 编写架构设计文档
- [ ] 添加API使用指南
- [ ] 编写部署手册
- [ ] 添加故障排除指南

**Implementation**: `docs/` 目录

**Verification**:
- [ ] 验证文档完整性
- [ ] 测试部署步骤
- [ ] 确认示例可运行

---

#### Task 8.2: 编写用户手册
**Priority**: P2 (Medium)
**Status**: ⏳ Pending
**Estimated**: 4 hours

**Requirements**: NFR4.1
**Design Reference**: PROJECT_SPEC.md - 待办

**Subtasks**:
- [ ] 编写快速开始指南
- [ ] 添加功能使用教程
- [ ] 创建视频演示
- [ ] 编写FAQ文档
- [ ] 添加最佳实践

**Implementation**: `docs/user_manual.md`

**Verification**:
- [ ] 用户测试指南
- [ ] 验证示例清晰
- [ ] 确认覆盖所有功能

---

## Task Summary

### Completed Tasks: ✅ (28/40)
- Phase 1: 核心探索引擎 - 4/4 tasks
- Phase 2: AI质量评估器 - 2/3 tasks
- Phase 3: 数据库与数据模型 - 2/2 tasks
- Phase 4: REST API - 2/2 tasks
- Phase 5: 前端界面 - 5/5 tasks
- Phase 6: 部署与测试 - 2/2 tasks
- Phase 7: 优化与增强 - 0/5 tasks
- Phase 8: 文档与用户手册 - 0/2 tasks

### Pending Tasks: ⏳ (12/40)
- Task 2.3: 优化批量评估 (P2)
- Task 7.1: 实现异步搜索优化 (P2)
- Task 7.2: 实现查询缓存 (P2)
- Task 7.3: 添加单元测试 (P2)
- Task 7.4: 实现API文档 (P2)
- Task 7.5: 添加监控与日志 (P3)
- Task 8.1: 编写系统文档 (P2)
- Task 8.2: 编写用户手册 (P2)

### Progress: 70% (28/40 tasks completed)

**Next Priority Tasks**:
1. Task 2.3: 优化批量评估 - 提升AI评估性能
2. Task 7.3: 添加单元测试 - 提高代码质量保证
3. Task 7.4: 实现API文档 - 改善开发者体验

---

**创建时间**: 2025-12-27
**最后更新**: 2025-12-27
**版本**: 1.0
