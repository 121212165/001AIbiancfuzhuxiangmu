# Design - AI Evaluator (AI评估器)

## Architecture Overview

### Component Architecture
```
┌─────────────────────────────────────┐
│         ValueEvaluator              │
│  - 统一评估接口                      │
│  - 提供商优先级链                    │
│  - 自动降级逻辑                      │
└──────────┬──────────────────────────┘
           │
      ┌────┼──────────────────────┐
      │    │                      │
┌─────▼────▼────┐  ┌──────────┐  ┌─▼──────────┐
│  ZhipuAI GLM  │  │SiliconFlow│  │ VolcEngine │
│  (Primary)    │  │(Backup 1) │  │ (Backup 2) │
└───────────────┘  └───────────┘  └────────────┘
      │                  │               │
      └──────────────────┼───────────────┘
                         │
                  ┌──────▼──────────┐
                  │  Fallback Logic │
                  │  (Heuristic)    │
                  └─────────────────┘
```

## Component Design

### 1. ValueEvaluator (主评估器)

**职责**: 协调多个AI提供商，处理评估和降级

**核心方法**:
```python
class ValueEvaluator:
    def evaluate(content: str, existing_nodes: List[Dict]) -> float:
        """评估内容价值
        Args:
            content: 待评估内容
            existing_nodes: 已有节点（用于上下文）
        Returns:
            价值评分 (0.0-1.0)
        """

    def _evaluate_with_provider(provider: str, content: str) -> float:
        """使用特定提供商评估"""

    def _evaluate_fallback(content: str) -> float:
        """启发式降级评分"""

    def _build_context(existing_nodes: List[Dict]) -> str:
        """构建评估上下文"""
```

**提供商优先级链**:
1. **ZhipuAI GLM-4-Flash** (免费，主要)
   - Base URL: `https://open.bigmodel.cn/api/paas/v4`
   - Model: `glm-4-flash`
   - Pricing: 免费

2. **SiliconFlow DeepSeek V3** (备用1)
   - Model: `deepseek-ai/DeepSeek-V3`
   - Pricing: ¥0.14/1M tokens

3. **VolcEngine 豆包** (备用2)
   - Model: `doubao-pro-32k`
   - Pricing: ¥0.69/1M tokens

4. **通义千问 Qwen** (备用3)
   - Model: `qwen-turbo`
   - Pricing: ¥0.57/1M tokens

5. **OpenRouter 免费模型** (最后备用)
   - Model: `google/gemma-7b-it:free`
   - Pricing: 免费

### 2. 评估Prompt设计

**标准Prompt**:
```python
prompt = f"""请评估这段内容的价值（0.0-1.0分）。

评估标准：
1. **新颖性** (0-1): 是否提供了新的信息或视角？
2. **质量** (0-1): 信息是否可信、有深度？
3. **潜力** (0-1): 是否能启发新的思考或发现？

参考背景（最近的发现）：
{context}

待评估内容：
{content[:2000]}

请只返回一个0.0到1.0之间的数字，不要其他内容。"""
```

**上下文构建**:
```python
def _build_context(existing_nodes: List[Dict]) -> str:
    """构建评估上下文
    返回最近5个高价值节点的摘要
    """
    high_value_nodes = [
        n for n in existing_nodes
        if n.get('value_score', 0) >= 0.7
    ][:5]

    context_parts = []
    for node in high_value_nodes:
        context_parts.append(
            f"- {node.get('title', '')}: {node.get('content', '')[:100]}..."
        )

    return "\n".join(context_parts) if context_parts else "（无已有发现）"
```

### 3. 评分解析逻辑

**正则表达式**:
```python
# 正确的正则模式（注意：\d 在raw string中应该写为 \d，不是 \\d）
score_pattern = r'0?\.\d+|1\.0|0|1'

# 匹配示例：
# - "0.8" -> 0.8
# - ".5" -> 0.5
# - "1.0" -> 1.0
# - "0" -> 0.0
# - "1" -> 1.0
```

**解析流程**:
```python
def _parse_score(response: str) -> float:
    """解析AI响应为评分"""
    # 1. 提取数字
    match = re.search(score_pattern, response)

    if match:
        score = float(match.group())
    else:
        # 2. 未匹配到，使用默认值
        logger.warning(f"Response '{response}' did not match pattern")
        score = 0.5

    # 3. 限制范围
    return max(0.0, min(1.0, score))
```

### 4. 降级策略

**自动降级流程**:
```python
def evaluate(content: str, existing_nodes: List[Dict] = None) -> float:
    """评估内容价值，支持自动降级"""

    # 优先级链
    providers = [
        ('zhipuai', settings.zhipuai_api_key),
        ('siliconflow', settings.siliconflow_api_key),
        ('volcengine', settings.volcengine_api_key),
        ('qwen', settings.qwen_api_key),
        ('openrouter', settings.openrouter_api_key),
    ]

    # 遍历提供商
    for provider_name, api_key in providers:
        if not api_key:
            continue  # 跳过未配置的提供商

        try:
            logger.info(f"Trying {provider_name}...")
            score = _evaluate_with_provider(provider_name, content, existing_nodes)
            logger.info(f"{provider_name} evaluation: {score}")
            return score  # 成功，返回评分

        except Exception as e:
            logger.error(f"{provider_name} failed: {e}")
            continue  # 失败，尝试下一个

    # 所有提供商都失败，使用启发式降级
    logger.warning("All providers failed, using heuristic fallback")
    return _evaluate_fallback(content, existing_nodes)
```

**启发式降级**:
```python
def _evaluate_fallback(content: str, existing_nodes: List[Dict] = None) -> float:
    """启发式降级评分
    基于内容特征的简单评分
    """
    score = 0.5  # 基础分

    # 长度奖励（内容越详细越好）
    if len(content) > 1000:
        score += 0.1
    elif len(content) > 500:
        score += 0.05

    # 关键词奖励
    keywords = ['novel', 'new', 'breakthrough', 'innovation', 'research']
    if any(kw in content.lower() for kw in keywords):
        score += 0.1

    # 去重惩罚（与已有内容相似）
    if existing_nodes:
        for node in existing_nodes:
            similarity = _calculate_similarity(content, node.get('content', ''))
            if similarity > 0.8:
                score -= 0.2
                break

    return max(0.0, min(1.0, score))
```

## Technology Stack

**Python SDK**:
- `openai`: 统一的API接口（兼容多个提供商）
- `httpx`: 异步HTTP客户端（用于API调用）
- `tenacity`: 重试逻辑

**配置管理**:
- `pydantic-settings`: 类型安全的配置
- `python-dotenv`: 环境变量加载

**日志**:
- `loguru`: 结构化日志

## Performance Optimization

### 优化1: 批量评估
```python
def evaluate_batch(contents: List[str], existing_nodes: List[Dict] = None) -> List[float]:
    """批量评估内容
    优化：减少API调用次数
    """
    # 当前：逐个评估
    # scores = [evaluate(c, existing_nodes) for c in contents]

    # 优化：批量请求（如果提供商支持）
    scores = []
    for content in contents:
        score = evaluate(content, existing_nodes)
        scores.append(score)

    return scores
```

### 优化2: 评估缓存
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_evaluate(content_hash: str, existing_nodes_hash: str) -> float:
    """带缓存的评估
    缓存key：内容哈希 + 上下文哈希
    """
    content = _decode_content(content_hash)
    existing_nodes = _decode_nodes(existing_nodes_hash)
    return evaluate(content, existing_nodes)
```

### 优化3: Token优化
```python
# 优化前：每次发送完整内容
prompt = f"评估：{content}"

# 优化后：截断到2000字符
prompt = f"评估：{content[:2000]}"

# 预估节省：50% tokens（对于长内容）
```

## Error Handling

### 重试策略
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def _evaluate_with_retry(provider: str, content: str) -> float:
    """带重试的评估"""
    return _evaluate_with_provider(provider, content)
```

### 超时控制
```python
def evaluate(content: str, timeout: int = 5) -> float:
    """带超时的评估"""
    try:
        # 设置API调用超时
        response = client.chat.completions.create(
            model=model,
            messages=[...],
            timeout=timeout  # 5秒超时
        )
        return _parse_score(response)
    except TimeoutError:
        logger.error(f"Evaluation timeout after {timeout}s")
        raise
```

## Monitoring

### 评估指标
- **成功率**: 成功评估次数 / 总评估次数
- **降级率**: 使用降级评估次数 / 总评估次数
- **平均响应时间**: 每个提供商的平均响应时间
- **评分分布**: 0.0-0.3, 0.3-0.5, 0.5-0.7, 0.7-1.0 的节点数
- **Token消耗**: 每日/每月token消耗统计

### 日志记录
```python
logger.info(f"Evaluation started: provider={provider}, content_length={len(content)}")
logger.info(f"Evaluation completed: score={score}, time={elapsed_time}s")
logger.warning(f"Evaluation failed: provider={provider}, error={error}")
```

---

**设计完成时间**: 2025-12-27
**设计师**: Claude Code
**版本**: 1.0
