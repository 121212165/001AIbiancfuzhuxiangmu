"""Value evaluator - assess the worth of discovered content."""

import os
from typing import List, Dict
from anthropic import Anthropic
from openai import OpenAI
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class ValueEvaluator:
    """Evaluates the value of discovered content."""

    def __init__(self):
        """Initialize evaluator with AI client."""
        # Priority: ZhipuAI (free) > SiliconFlow > VolcEngine > Qwen > OpenRouter > Anthropic > OpenAI > Fallback
        if settings.zhipuai_api_key:
            self.client = OpenAI(
                api_key=settings.zhipuai_api_key,
                base_url=settings.zhipuai_base_url
            )
            self.provider = "zhipuai"
            self.model = settings.zhipuai_model
        elif settings.siliconflow_api_key:
            self.client = OpenAI(
                api_key=settings.siliconflow_api_key,
                base_url=settings.siliconflow_base_url
            )
            self.provider = "siliconflow"
            self.model = settings.siliconflow_model
        elif settings.volcengine_api_key:
            self.client = OpenAI(
                api_key=settings.volcengine_api_key,
                base_url=settings.volcengine_base_url
            )
            self.provider = "volcengine"
            self.model = settings.volcengine_model
        elif settings.qwen_api_key:
            self.client = OpenAI(
                api_key=settings.qwen_api_key,
                base_url=settings.qwen_base_url
            )
            self.provider = "qwen"
            self.model = settings.qwen_model
        elif settings.openrouter_api_key:
            self.client = OpenAI(
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url
            )
            self.provider = "openrouter"
            self.model = settings.openrouter_model
        elif settings.anthropic_api_key:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.provider = "anthropic"
        elif settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.provider = "openai"
        else:
            logger.warning("No AI API key found! Using fallback evaluation.")
            self.client = None
            self.provider = "fallback"

    def evaluate(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """
        Evaluate content value score (0-1).

        Factors:
        - Novelty: How different from existing content
        - Quality: Information density, credibility
        - Potential: Inspiration/connections potential
        """
        if self.provider == "zhipuai":
            return self._evaluate_with_zhipuai(content, existing_nodes)
        elif self.provider == "siliconflow":
            return self._evaluate_with_siliconflow(content, existing_nodes)
        elif self.provider == "volcengine":
            return self._evaluate_with_volcengine(content, existing_nodes)
        elif self.provider == "qwen":
            return self._evaluate_with_qwen(content, existing_nodes)
        elif self.provider == "openrouter":
            return self._evaluate_with_openrouter(content, existing_nodes)
        elif self.provider == "anthropic":
            return self._evaluate_with_claude(content, existing_nodes)
        elif self.provider == "openai":
            return self._evaluate_with_gpt(content, existing_nodes)
        else:
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_with_zhipuai(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Evaluate using ZhipuAI GLM."""
        try:
            context = self._build_context(existing_nodes)

            prompt = f"""请评估这段内容的价值（0.0-1.0分）。

评估标准：
1. 新颖性：是否提供了新的信息或视角？
2. 质量：信息是否可信、有深度？
3. 潜力：是否能启发新的思考或发现？

参考背景（最近的发现）：
{context}

待评估内容：
{content[:2000]}

请只返回一个0.0到1.0之间的数字，不要其他内容。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            logger.info(f"ZhipuAI raw response: '{result}'")
            # Extract number from response (fixed regex)
            import re
            match = re.search(r'0?\.\d+|1\.0|0|1', result)
            if match:
                score = float(match.group())
            else:
                logger.warning(f"ZhipuAI response '{result}' did not match pattern, using default 0.5")
                score = 0.5

            logger.info(f"ZhipuAI evaluation: {score} for content length {len(content)}")
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"ZhipuAI evaluation failed: {e}")
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_with_claude(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Evaluate using Claude."""
        try:
            context = self._build_context(existing_nodes)

            prompt = f"""You are an expert at evaluating the value of information for breaking out of filter bubbles.

Rate this content on a scale of 0.0 to 1.0 based on:
1. Novelty (0-1): How new/unusual is this information?
2. Quality (0-1): Is it credible, substantive, and well-articulated?
3. Serendipity Potential (0-1): Could this lead to unexpected discoveries or connections?

Context (recent discoveries):
{context}

Content to evaluate:
{content[:2000]}

Return ONLY a single number between 0.0 and 1.0, nothing else.
"""

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            result = message.content[0].text.strip()
            score = float(result)
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"Claude evaluation failed: {e}")
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_with_openrouter(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Evaluate using OpenRouter (xiaomi model)."""
        try:
            context = self._build_context(existing_nodes)

            prompt = f"""请评估这段内容的价值（0.0-1.0分）。

评估标准：
1. 新颖性：是否提供了新的信息或视角？
2. 质量：信息是否可信、有深度？
3. 潜力：是否能启发新的思考或发现？

参考背景（最近的发现）：
{context}

待评估内容：
{content[:2000]}

请只返回一个0.0到1.0之间的数字，不要其他内容。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            # Extract number from response
            import re
            match = re.search(r'0?\.\d+|1\.0|0|1', result)
            if match:
                score = float(match.group())
            else:
                score = 0.5

            logger.info(f"OpenRouter evaluation: {score} for content length {len(content)}")
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"OpenRouter evaluation failed: {e}")
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_with_volcengine(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Evaluate using VolcEngine (Doubao)."""
        try:
            context = self._build_context(existing_nodes)

            prompt = f"""请评估这段内容的价值（0.0-1.0分）。

评估标准：
1. 新颖性：是否提供了新的信息或视角？
2. 质量：信息是否可信、有深度？
3. 潜力：是否能启发新的思考或发现？

参考背景（最近的发现）：
{context}

待评估内容：
{content[:2000]}

请只返回一个0.0到1.0之间的数字，不要其他内容。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            # Extract number from response
            import re
            match = re.search(r'0?\.\d+|1\.0|0|1', result)
            if match:
                score = float(match.group())
            else:
                score = 0.5

            logger.info(f"VolcEngine evaluation: {score} for content length {len(content)}")
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"VolcEngine evaluation failed: {e}")
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_with_qwen(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Evaluate using Qwen (Alibaba Cloud)."""
        try:
            context = self._build_context(existing_nodes)

            prompt = f"""请评估这段内容的价值（0.0-1.0分）。

评估标准：
1. 新颖性：是否提供了新的信息或视角？
2. 质量：信息是否可信、有深度？
3. 潜力：是否能启发新的思考或发现？

参考背景（最近的发现）：
{context}

待评估内容：
{content[:2000]}

请只返回一个0.0到1.0之间的数字，不要其他内容。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            # Extract number from response (fixed regex)
            import re
            match = re.search(r'0?\.\d+|1\.0|0|1', result)
            if match:
                score = float(match.group())
            else:
                score = 0.5

            logger.info(f"Qwen evaluation: {score} for content length {len(content)}")
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"Qwen evaluation failed: {e}")
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_with_siliconflow(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Evaluate using SiliconFlow DeepSeek."""
        try:
            context = self._build_context(existing_nodes)

            prompt = f"""请评估这段内容的价值（0.0-1.0分）。

评估标准：
1. 新颖性：是否提供了新的信息或视角？
2. 质量：信息是否可信、有深度？
3. 潜力：是否能启发新的思考或发现？

参考背景（最近的发现）：
{context}

待评估内容：
{content[:2000]}

请只返回一个0.0到1.0之间的数字，不要其他内容。
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            # Extract number from response (handle cases where model adds text)
            import re
            match = re.search(r'0?\.\d+|1\.0|0|1', result)
            if match:
                score = float(match.group())
            else:
                score = 0.5

            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"SiliconFlow evaluation failed: {e}")
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_with_gpt(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Evaluate using GPT."""
        try:
            context = self._build_context(existing_nodes)

            prompt = f"""Rate this content's value on a scale of 0.0 to 1.0.

Context (recent discoveries):
{context}

Content:
{content[:2000]}

Consider: novelty, quality, and potential for unexpected insights.
Return ONLY a number between 0.0 and 1.0.
"""

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            score = float(result)
            return max(0.0, min(1.0, score))

        except Exception as e:
            logger.error(f"GPT evaluation failed: {e}")
            return self._evaluate_fallback(content, existing_nodes)

    def _evaluate_fallback(self, content: str, existing_nodes: List[Dict] = None) -> float:
        """Fallback evaluation without AI."""
        # Heuristic-based scoring
        score = 0.5  # Base score

        # Length bonus (prefer substantive content)
        if len(content) > 500:
            score += 0.1
        elif len(content) < 100:
            score -= 0.2

        # Check for "filler" words (lower quality)
        filler_words = ['click here', 'subscribe', 'buy now', 'limited time']
        if any(word in content.lower() for word in filler_words):
            score -= 0.3

        # Check for technical/academic indicators (higher quality)
        quality_indicators = ['research', 'study', 'analysis', 'data', 'experiment']
        if any(word in content.lower() for word in quality_indicators):
            score += 0.2

        return max(0.0, min(1.0, score))

    def _build_context(self, existing_nodes: List[Dict]) -> str:
        """Build context string from existing nodes."""
        if not existing_nodes:
            return "No previous discoveries."

        recent = existing_nodes[:5]  # Only show recent 5
        context_lines = []
        for i, node in enumerate(recent, 1):
            context_lines.append(f"{i}. {node.get('content', '')[:100]}...")

        return "\n".join(context_lines)

    def extract_tags(self, content: str) -> List[str]:
        """Extract tags from content."""
        if self.provider == "fallback":
            return self._extract_tags_fallback(content)

        try:
            if self.provider == "zhipuai":
                prompt = f"""从这段内容中提取3-5个标签/关键词。

内容：
{content[:1000]}

只返回逗号分隔的标签，不要其他内容。
例如：机器学习, 研究, 创新
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0
                )
                result = response.choices[0].message.content.strip()
                return [tag.strip() for tag in result.split(",")[:5]]

            if self.provider == "volcengine":
                prompt = f"""从这段内容中提取3-5个标签/关键词。

内容：
{content[:1000]}

只返回逗号分隔的标签，不要其他内容。
例如：机器学习, 研究, 创新
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0
                )
                result = response.choices[0].message.content.strip()
                return [tag.strip() for tag in result.split(",")[:5]]

            if self.provider == "qwen":
                prompt = f"""从这段内容中提取3-5个标签/关键词。

内容：
{content[:1000]}

只返回逗号分隔的标签，不要其他内容。
例如：机器学习, 研究, 创新
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0
                )
                result = response.choices[0].message.content.strip()
                return [tag.strip() for tag in result.split(",")[:5]]

            if self.provider == "openrouter":
                prompt = f"""从这段内容中提取3-5个标签/关键词。

内容：
{content[:1000]}

只返回逗号分隔的标签，不要其他内容。
例如：机器学习, 研究, 创新
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0
                )
                result = response.choices[0].message.content.strip()
                return [tag.strip() for tag in result.split(",")[:5]]

            if self.provider == "siliconflow":
                prompt = f"""从这段内容中提取3-5个标签/关键词。

内容：
{content[:1000]}

只返回逗号分隔的标签，不要其他内容。
例如：机器学习, 研究, 创新
"""
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0
                )
                result = response.choices[0].message.content.strip()
                return [tag.strip() for tag in result.split(",")[:5]]

            if self.provider == "anthropic":
                prompt = f"""Extract 3-5 concise tags/keywords from this content.

Content:
{content[:1000]}

Return only tags separated by commas, nothing else.
Example: machine learning, research, innovation
"""
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=50,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = message.content[0].text.strip()
                return [tag.strip() for tag in result.split(",")[:5]]

            elif self.provider == "openai":
                prompt = f"Extract 3-5 tags from: {content[:1000]}\n\nReturn comma-separated tags only."
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0
                )
                result = response.choices[0].message.content.strip()
                return [tag.strip() for tag in result.split(",")[:5]]

        except Exception as e:
            logger.error(f"Tag extraction failed: {e}")

        return self._extract_tags_fallback(content)

    def _extract_tags_fallback(self, content: str) -> List[str]:
        """Fallback tag extraction using simple heuristics."""
        words = content.lower().split()
        # Common tech/science keywords
        keywords = ['ai', 'ml', 'research', 'data', 'science', 'tech',
                   'python', 'algorithm', 'model', 'system', 'code']
        found = [kw for kw in keywords if kw in content.lower()]
        return found[:5] if found else ['general']


# Alias for compatibility
Evaluator = ValueEvaluator
