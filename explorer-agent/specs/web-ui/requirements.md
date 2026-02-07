# Requirements - Web UI (Web界面)

## User Story
作为系统用户，我需要一个直观的Web界面，能够：
1. 查看探索发现的节点和路径
2. 控制探索过程和策略
3. 管理探索种子池
4. 分析探索质量和统计

## EARS Format Requirements

### EPIC: 直观的探索管理界面

**Feature 1: 探索控制面板**
- AS a 系统用户
- I WANT TO 控制探索过程
- SO THAT 可以灵活启动和管理探索任务

**Acceptance Criteria:**
- AC1.1: 选择探索策略 (random/edge/graph/mixed)
- AC1.2: 设置迭代次数 (1-10次)
- AC1.3: 启动探索按钮
- AC1.4: 显示任务状态和进度

**Feature 2: 节点发现展示**
- AS a 研究者
- I WANT TO 查看发现的内容节点
- SO THAT 了解探索发现的价值内容

**Acceptance Criteria:**
- AC2.1: 显示节点列表 (标题、内容、来源、类型)
- AC2.2: 显示价值评分 (emoji标识)
- AC2.3: 支持按评分过滤节点
- AC2.4: 显示节点详情 (可展开)
- AC2.5: 显示发现时间和标签

**Feature 3: 探索路径可视化**
- AS a 研究者
- I WANT TO 查看探索路径
- SO THAT 理解知识发现过程

**Acceptance Criteria:**
- AC3.1: 显示探索路径列表
- AC3.2: 显示路径节点序列
- AC3.3: 显示路径总价值
- AC3.4: 支持按路径价值过滤
- AC3.5: 提供"沿路径继续探索"按钮

**Feature 4: 质量分析面板**
- AS a 质量管理者
- I WANT TO 分析探索质量
- SO THAT 评估系统表现

**Acceptance Criteria:**
- AC4.1: 显示价值分数分布直方图
- AC4.2: 显示评分统计指标 (平均、最高、最低、中位数)
- AC4.3: 显示评估系统说明
- AC4.4: 显示低价值内容示例

**Feature 5: 种子管理界面**
- AS a 系统管理员
- I WANT TO 管理探索种子池
- SO THAT 控制探索方向

**Acceptance Criteria:**
- AC5.1: 显示当前种子列表
- AC5.2: 显示种子优先级和尝试次数
- AC5.3: 支持单个种子探索
- AC5.4: 支持批量添加种子
- AC5.5: 支持清空所有种子
- AC5.6: 支持随机添加种子

**Feature 6: 统计信息展示**
- AS a 系统用户
- I WANT TO 查看系统统计
- SO THAT 了解探索进度

**Acceptance Criteria:**
- AC6.1: 显示总节点数
- AC6.2: 显示总路径数
- AC6.3: 显示待探索种子数
- AC6.4: 显示平均价值分
- AC6.5: 显示质量分布 (高/中/低价值节点数)

## Non-Functional Requirements

### Performance
- NFR1.1: 页面加载时间 < 3秒
- NFR1.2: 数据刷新时间 < 2秒
- NFR1.3: 实现数据缓存 (TTL=60s)

### Usability
- NFR2.1: 界面直观易用
- NFR2.2: 响应式布局 (支持桌面)
- NFR2.3: 清晰的视觉反馈
- NFR2.4: 错误提示友好

### Reliability
- NFR3.1: API失败时显示错误
- NFR3.2: 数据加载中显示loading
- NFR3.3: 操作后自动刷新数据

### Aesthetics
- NFR4.1: 清晰的视觉层次
- NFR4.2: 一致的颜色方案
- NFR4.3: 适当的图标和emoji使用

## Constraints
- C1: 使用Streamlit框架 (Python)
- C2: 前端无独立后端 (调用FastAPI)
- C3: 数据实时性要求不高 (60s缓存可接受)
- C4: 部署在Docker容器中

## Assumptions
- A1: 用户有基础技术背景
- A2: 用户理解探索和质量评分概念
- A3: 桌面浏览器访问为主
- A4: API响应时间 < 1秒
