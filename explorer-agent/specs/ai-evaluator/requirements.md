# Requirements - AI Evaluator (AI评估器)

## User Story
作为探索系统，我需要一个可靠的内容价值评估器，能够：
1. 准确评估内容的新颖性、质量和潜力
2. 在多个AI提供商之间自动切换和降级
3. 保持评估的一致性和可解释性
4. 优化评估速度和成本

## EARS Format Requirements

### EPIC: 智能内容价值评估系统

**Feature 1: 多提供商支持**
- AS a 系统管理员
- I WANT TO 支持多个AI评估提供商
- SO THAT 系统可以在单个API失败时自动切换

**Acceptance Criteria:**
- AC1.1: 支持智谱AI GLM-4-Flash (免费，主要)
- AC1.2: 支持硅基流动 DeepSeek V3 (备用)
- AC1.3: 支持火山引擎 豆包 (备用)
- AC1.4: 支持通义千问 Qwen (备用)
- AC1.5: 支持OpenRouter免费模型 (最后备用)
- AC1.6: 实现自动降级机制（主API失败时切换）

**Feature 2: 评估标准一致性**
- AS a 质量控制系统
- I WANT TO 统一的评估标准和评分体系
- SO THAT 不同提供商的评估结果具有可比性

**Acceptance Criteria:**
- AC2.1: 评估标准包括：新颖性(0-1)、质量(0-1)、潜力(0-1)
- AC2.2: 最终评分范围：0.0-1.0
- AC2.3: 评分阈值：MIN_VALUE_SCORE = 0.1 (低于此分不保存)
- AC2.4: 提供评分解释和理由

**Feature 3: 性能优化**
- AS a 高性能系统
- I WANT TO 优化AI评估的速度和成本
- SO THAT 系统可以快速处理大量内容

**Acceptance Criteria:**
- AC3.1: 单次评估响应时间 < 5秒
- AC3.2: 支持批量评估（一次评估多个内容）
- AC3.3: 实现评估结果缓存
- AC3.4: 优化prompt长度以减少token消耗

**Feature 4: 错误处理与可靠性**
- AS a 可靠系统
- I WANT TO 健壮的错误处理和降级策略
- SO THAT 系统在API故障时仍能继续运行

**Acceptance Criteria:**
- AC4.1: API超时自动重试（最多3次）
- AC4.2: API失败时自动切换到下一个提供商
- AC4.3: 所有提供商都失败时使用启发式评分
- AC4.4: 记录所有评估失败和降级事件

## Non-Functional Requirements

### Performance
- NFR1.1: 单次评估耗时 < 5秒
- NFR1.2: 批量评估(10个)耗时 < 30秒
- NFR1.3: 评估缓存命中率 > 30%

### Reliability
- NFR2.1: API失败时自动降级时间 < 1秒
- NFR2.2: 评估成功率 > 95% (包括降级)
- NFR2.3: 评估日志完整记录所有尝试

### Scalability
- NFR3.1: 支持并发评估（最多10个同时请求）
- NFR3.2: 可轻松添加新的AI提供商
- NFR3.3: 评估配置可热更新（无需重启）

### Usability
- NFR4.1: 评估结果可解释（显示评分理由）
- NFR4.2: 评估配置清晰易懂
- NFR4.3: 评估状态实时可见

## Constraints
- C1: 免费API可能有速率限制
- C2: 不同AI模型的评分标准可能不同
- C3: API密钥需要安全管理
- C4: Token消耗需要监控和控制

## Assumptions
- A1: AI评估结果基本可靠（平均误差 < 0.2）
- A2: 用户理解评分是主观的
- A3: 免费API足够用于测试和开发
- A4: 可以通过prompt工程减少评分差异
