"""Thinking Engine - deep analysis and mining of low-quality content."""

import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI
from anthropic import Anthropic

from app.db.session import SessionLocal
from app.models import LowQualityPool, Insight, ThinkingProcess, Frontier, Node
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ThinkingEngine:
    """Deep thinking engine - mines value from low-quality content."""

    def __init__(self):
        """Initialize thinking engine with AI client."""
        # Use stronger model for deeper thinking
        # Priority: Claude Opus > GPT-4 > ZhipuAI (fallback)
        if settings.anthropic_api_key:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.provider = "anthropic"
            self.model = "claude-3-5-sonnet-20241022"  # Can be upgraded to opus
        elif settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.provider = "openai"
            self.model = "gpt-4-turbo-preview"
        elif settings.zhipuai_api_key:
            self.client = OpenAI(
                api_key=settings.zhipuai_api_key,
                base_url=settings.zhipuai_base_url
            )
            self.provider = "zhipuai"
            self.model = settings.zhipuai_model
        else:
            logger.warning("No AI API key found for Thinker!")
            self.client = None
            self.provider = "fallback"

    def process_low_quality_pool(self, batch_size: int = 10, mode: str = "auto") -> Dict:
        """
        Process low-quality content pool.

        Args:
            batch_size: Number of items to process
            mode: 'auto' (choose best strategy), 'mine_gems', 'synthesize', 'discover_connections'

        Returns:
            Dict with processing results
        """
        db = SessionLocal()
        results = {
            'processed_count': 0,
            'insights_created': 0,
            'gems_found': 0,
            'connections_discovered': 0,
            'new_seeds_added': 0,
            'processing_time': 0,
            'errors': []
        }

        try:
            start_time = time.time()

            # Get unprocessed low-quality items
            items = db.query(LowQualityPool).filter_by(processed=False).limit(batch_size).all()

            if not items:
                logger.info("No unprocessed items in low-quality pool")
                return results

            logger.info(f"Thinker: Processing {len(items)} low-quality items")

            # Group items by tags for better synthesis
            grouped = self._group_by_tags(items)

            # Process based on mode
            if mode == "auto":
                # Choose best strategy based on item count and diversity
                if len(items) >= 5:
                    # Have enough items for synthesis
                    strategy_results = self.synthesize_insights(items, db)
                elif len(items) >= 3:
                    # Try to find connections
                    strategy_results = self.discover_hidden_connections(items, db)
                else:
                    # Mine individual gems
                    strategy_results = self.mine_hidden_gems(items, db)
            elif mode == "mine_gems":
                strategy_results = self.mine_hidden_gems(items, db)
            elif mode == "synthesize":
                strategy_results = self.synthesize_insights(items, db)
            elif mode == "discover_connections":
                strategy_results = self.discover_hidden_connections(items, db)
            else:
                raise ValueError(f"Unknown mode: {mode}")

            # Update results
            results.update(strategy_results)

            # Mark items as processed
            for item in items:
                item.processed = True
                item.processing_attempts += 1

            db.commit()

            results['processing_time'] = time.time() - start_time
            logger.info(f"Thinker: Processing complete - {results}")

        except Exception as e:
            logger.error(f"Thinker processing failed: {e}")
            db.rollback()
            results['errors'].append(str(e))
        finally:
            db.close()

        return results

    def mine_hidden_gems(self, items: List[LowQualityPool], db: Session) -> Dict:
        """
        Mine hidden gems - extract valuable parts from low-quality content.

        Even low-scoring papers may have valuable concepts, methods, or data points.
        """
        logger.info(f"Thinker: Mining hidden gems from {len(items)} items")

        results = {
            'processed_count': len(items),
            'insights_created': 0,
            'gems_found': 0,
            'connections_discovered': 0,
            'new_seeds_added': 0,
        }

        for item in items:
            try:
                # Use AI to extract valuable parts
                prompt = f"""你是一个擅长发现价值的专家。请仔细阅读以下内容，虽然它整体评分不高，但可能包含有价值的部分。

任务：
1. 识别其中真正有价值的概念、方法、数据点或洞察
2. 提取出这些"隐藏的宝石"
3. 用简洁的语言重新表述，使其价值更清晰

内容标题：{item.title}
内容来源：{item.source}
原始评分：{item.original_score}
标签：{', '.join(item.tags or [])}

内容：
{item.content[:3000]}

请按以下格式回复：

## 隐藏宝石
[描述你发现的1-3个有价值的部分，每个用一段话说明]

## 重新评估
[基于这些宝石，给这篇内容一个新的评分（0-1）和简要理由]

## 探索建议
[基于这些宝石，建议2-3个新的探索方向/关键词]
"""

                thinking_result = self._call_ai(prompt)

                # Parse the response
                gems_part = self._extract_section(thinking_result, "隐藏宝石")
                reassessment = self._extract_section(thinking_result, "重新评估")
                suggestions = self._extract_section(thinking_result, "探索建议")

                if gems_part:
                    # Create insight for the gems
                    insight = Insight(
                        source_node_ids=[item.id],
                        insight_content=gems_part,
                        insight_type="hidden_gem",
                        value_score=self._parse_score(reassessment) or max(item.original_score + 0.2, 0.5),
                        title=f"Hidden Gem: {item.title[:50]}",
                        reasoning=reassessment,
                        meta_data={
                            "original_score": item.original_score,
                            "source": item.source,
                            "original_type": item.type
                        }
                    )
                    db.add(insight)
                    db.flush()
                    results['gems_found'] += 1
                    results['insights_created'] += 1

                    # Add new seeds from suggestions
                    if suggestions:
                        self._add_seeds_from_text(suggestions, db, insight.id)
                        results['new_seeds_added'] += 1

                    # Record thinking process
                    self._record_thinking_process(
                        db=db,
                        session_type="mine_gems",
                        input_ids=[item.id],
                        prompt=prompt,
                        result=thinking_result,
                        insight_ids=[insight.id],
                        processing_time=0
                    )

            except Exception as e:
                logger.error(f"Failed to mine gems from item {item.id}: {e}")
                results['errors'] = results.get('errors', [])
                results['errors'].append(str(e))

        return results

    def synthesize_insights(self, items: List[LowQualityPool], db: Session) -> Dict:
        """
        Synthesize insights from multiple low-quality items.

        Individual items may seem insignificant, but together they might reveal patterns or trends.
        """
        logger.info(f"Thinker: Synthesizing insights from {len(items)} items")

        results = {
            'processed_count': len(items),
            'insights_created': 0,
            'gems_found': 0,
            'connections_discovered': 0,
            'new_seeds_added': 0,
        }

        if len(items) < 2:
            logger.info("Not enough items to synthesize")
            return results

        try:
            # Group by topic/tags for better synthesis
            grouped = self._group_by_tags(items)

            for group_name, group_items in grouped.items():
                if len(group_items) < 2:
                    continue

                # Build context from group
                context = "\n\n".join([
                    f"### {item.title}\n{item.content[:500]}\n评分: {item.original_score}"
                    for item in group_items[:5]  # Limit to 5 items per synthesis
                ])

                prompt = f"""你是一个擅长综合分析的专家。以下{len(group_items)}篇内容虽然单独评分不高，但它们可能共同揭示了某个趋势、模式或洞察。

任务：
1. 识别这些内容的共同主题
2. 综合它们，提炼出比单独任何一篇都更有价值的洞察
3. 指出这个综合洞察的价值所在

内容：
{context}

请按以下格式回复：

## 共同主题
[这些内容的共同主题是什么]

## 综合洞察
[基于这些内容，提炼出的高价值洞察]

## 价值评估
[给这个综合洞察评分（0-1）和说明理由]

## 新探索方向
[基于这个洞察，建议2-3个值得深入探索的方向]
"""

                thinking_result = self._call_ai(prompt)

                # Parse response
                theme = self._extract_section(thinking_result, "共同主题")
                insight_content = self._extract_section(thinking_result, "综合洞察")
                value_assessment = self._extract_section(thinking_result, "价值评估")
                new_directions = self._extract_section(thinking_result, "新探索方向")

                if insight_content:
                    # Create synthesized insight
                    insight = Insight(
                        source_node_ids=[item.id for item in group_items],
                        insight_content=f"主题: {theme}\n\n{insight_content}",
                        insight_type="synthesis",
                        value_score=self._parse_score(value_assessment) or 0.7,
                        title=f"Synthesis: {theme[:50]}",
                        reasoning=value_assessment,
                        meta_data={
                            "item_count": len(group_items),
                            "original_scores": [item.original_score for item in group_items]
                        }
                    )
                    db.add(insight)
                    db.flush()
                    results['insights_created'] += 1

                    # Add new seeds
                    if new_directions:
                        self._add_seeds_from_text(new_directions, db, insight.id)
                        results['new_seeds_added'] += 1

                    # Record thinking process
                    self._record_thinking_process(
                        db=db,
                        session_type="synthesize",
                        input_ids=[item.id for item in group_items],
                        prompt=prompt,
                        result=thinking_result,
                        insight_ids=[insight.id],
                        processing_time=0
                    )

        except Exception as e:
            logger.error(f"Failed to synthesize insights: {e}")
            results['errors'] = results.get('errors', [])
            results['errors'].append(str(e))

        return results

    def discover_hidden_connections(self, items: List[LowQualityPool], db: Session) -> Dict:
        """
        Discover hidden connections between low-quality items.

        Find relationships, citations, or conceptual links that weren't obvious.
        """
        logger.info(f"Thinker: Discovering hidden connections between {len(items)} items")

        results = {
            'processed_count': len(items),
            'insights_created': 0,
            'gems_found': 0,
            'connections_discovered': 0,
            'new_seeds_added': 0,
        }

        if len(items) < 2:
            return results

        try:
            # Build summary of all items
            summaries = []
            for item in items[:10]:  # Limit to 10 items
                summaries.append(f"- {item.title[:60]}... (评分: {item.original_score}, 标签: {', '.join(item.tags or [])})")

            context = "\n".join(summaries)

            prompt = f"""你是一个擅长发现隐藏关联的专家。以下{len(items)}篇内容可能存在不明显的关联。

任务：
1. 识别这些内容之间的潜在关联（引用关系、概念关联、方法相似等）
2. 找出未被发现的连接
3. 指出这些关联的价值

内容列表：
{context}

请按以下格式回复：

## 发现的关联
[描述你发现的1-3个关联，说明哪些内容相关，如何相关]

## 关联价值
[说明这些关联为什么有价值，可能揭示什么]

## 探索建议
[基于这些关联，建议2-3个新的探索关键词]
"""

            thinking_result = self._call_ai(prompt)

            # Parse response
            connections = self._extract_section(thinking_result, "发现的关联")
            value = self._extract_section(thinking_result, "关联价值")
            suggestions = self._extract_section(thinking_result, "探索建议")

            if connections:
                # Create connection insight
                insight = Insight(
                    source_node_ids=[item.id for item in items],
                    insight_content=f"{connections}\n\n价值: {value}",
                    insight_type="connection",
                    value_score=0.6,  # Connections have moderate value
                    title=f"Connections: {len(items)} items",
                    reasoning=value,
                    meta_data={"item_count": len(items)}
                )
                db.add(insight)
                db.flush()
                results['connections_discovered'] = 1
                results['insights_created'] += 1

                # Add new seeds
                if suggestions:
                    self._add_seeds_from_text(suggestions, db, insight.id)
                    results['new_seeds_added'] += 1

                # Record thinking process
                self._record_thinking_process(
                    db=db,
                    session_type="discover_connections",
                    input_ids=[item.id for item in items],
                    prompt=prompt,
                    result=thinking_result,
                    insight_ids=[insight.id],
                    processing_time=0
                )

        except Exception as e:
            logger.error(f"Failed to discover connections: {e}")
            results['errors'] = results.get('errors', [])
            results['errors'].append(str(e))

        return results

    def _call_ai(self, prompt: str) -> str:
        """Call AI model for thinking."""
        if self.provider == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,  # Higher temperature for more creative thinking
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text

        elif self.provider in ["openai", "zhipuai"]:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content

        else:
            # Fallback
            return "AI not available for thinking"

    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract a section from AI response."""
        lines = text.split('\n')
        in_section = False
        section_content = []

        for line in lines:
            if section_name in line:
                in_section = True
                continue
            elif in_section and line.startswith('##'):
                break
            elif in_section:
                section_content.append(line.strip())

        result = '\n'.join(section_content).strip()
        return result if result else None

    def _parse_score(self, text: Optional[str]) -> Optional[float]:
        """Parse score from text."""
        if not text:
            return None
        import re
        match = re.search(r'0?\.\d+|1\.0|0|1', text)
        if match:
            return float(match.group())
        return None

    def _group_by_tags(self, items: List[LowQualityPool]) -> Dict[str, List[LowQualityPool]]:
        """Group items by tags for better processing."""
        grouped = {"general": []}

        for item in items:
            tags = item.tags or []
            if tags:
                # Use first tag as group name
                group_name = tags[0]
                if group_name not in grouped:
                    grouped[group_name] = []
                grouped[group_name].append(item)
            else:
                grouped["general"].append(item)

        return grouped

    def _add_seeds_from_text(self, text: str, db: Session, insight_id: int):
        """Extract and add new frontier seeds from text."""
        # Simple extraction: look for keywords/phrases
        keywords = text.replace('\n', ' ').split()

        # Filter for meaningful seeds (2+ words, tech terms)
        seeds = []
        for i in range(len(keywords) - 1):
            phrase = f"{keywords[i]} {keywords[i+1]}"
            if len(phrase) > 5 and phrase[0].isalpha():
                seeds.append(phrase)

        # Add unique seeds
        added = 0
        for seed in seeds[:5]:  # Limit to 5 seeds
            existing = db.query(Frontier).filter(Frontier.seed == seed).first()
            if not existing:
                frontier = Frontier(
                    seed=seed,
                    priority=0.7,  # Higher priority for Thinker-generated seeds
                    source_node_id=insight_id
                )
                db.add(frontier)
                added += 1

        logger.info(f"Added {added} new seeds from insight {insight_id}")

    def _record_thinking_process(
        self,
        db: Session,
        session_type: str,
        input_ids: List[int],
        prompt: str,
        result: str,
        insight_ids: List[int],
        processing_time: float
    ):
        """Record thinking process for transparency."""
        process = ThinkingProcess(
            session_type=session_type,
            input_low_quality_ids=input_ids,
            thinking_prompt=prompt[:1000],  # Truncate long prompts
            thinking_result=result[:5000],  # Truncate long results
            extracted_insights=insight_ids,
            processing_time=processing_time,
            ai_model_used=f"{self.provider}:{self.model}",
            status="completed"
        )
        db.add(process)


# Singleton instance
thinking_engine = ThinkingEngine()

# Alias for compatibility
Thinker = ThinkingEngine
