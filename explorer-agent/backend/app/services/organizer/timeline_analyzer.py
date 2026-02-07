"""
Timeline Analyzer for Organizer Agent
"""
from typing import Dict, List, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.knowledge import TimelineEvent, TrendMetric
from app.models.node import Node as ExplorationNode
from app.models.insight import Insight
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class TimelineAnalyzer:
    """
    Timeline analyzer

    Analyzes temporal patterns and trends in discovered content
    """

    def __init__(self):
        pass

    def analyze(self, items: List[Any]) -> Dict[str, Any]:
        """
        Analyze timeline of items

        Args:
            items: List of nodes and insights

        Returns:
            {
                "events": List[Dict],
                "metrics": {...}
            }
        """
        if not items:
            return {
                "events": [],
                "metrics": {"events_found": 0}
            }

        db = next(get_db())

        try:
            # Group items by date
            events_data = self._create_timeline_events(db, items)

            return {
                "events": [
                    {
                        "id": e.id,
                        "date": e.event_date.isoformat(),
                        "type": e.event_type,
                        "title": e.title,
                        "description": e.description,
                        "impact": e.impact_level
                    }
                    for e in events_data
                ],
                "metrics": {
                    "events_found": len(events_data)
                }
            }

        except Exception as e:
            logger.error(f"Failed to analyze timeline: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()

    def identify_trends(self, items: List[Any]) -> Dict[str, Any]:
        """
        Identify trends from items

        Args:
            items: List of nodes and insights

        Returns:
            {
                "rising": List[str],
                "stable": List[str],
                "declining": List[str],
                "emerging": List[str]
            }
        """
        if not items:
            return {
                "rising": [],
                "stable": [],
                "declining": [],
                "emerging": []
            }

        db = next(get_db())

        try:
            # Extract and count keywords
            keyword_counts = self._extract_keywords(items)

            # Create trend metrics
            trends_data = self._create_trend_metrics(db, keyword_counts)

            # Categorize by frequency
            rising = [k.keyword for k in trends_data if k.frequency >= 3]
            stable = [k.keyword for k in trends_data if 1 <= k.frequency < 3]
            declining = []  # Requires historical data

            return {
                "rising": rising,
                "stable": stable,
                "declining": declining,
                "emerging": []  # Requires historical comparison
            }

        except Exception as e:
            logger.error(f"Failed to identify trends: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()

    def _create_timeline_events(self, db: Session, items: List[Any]) -> List[TimelineEvent]:
        """Create timeline events from items"""
        events = []

        for item in items:
            if not hasattr(item, 'created_at') or not item.created_at:
                continue

            event_date = item.created_at.date() if isinstance(item.created_at, datetime) else item.created_at

            event = TimelineEvent(
                event_date=event_date,
                event_type="publication" if hasattr(item, 'source') else "insight",
                title=item.title if hasattr(item, 'title') else "New Item",
                description=item.content[:200] if hasattr(item, 'content') and item.content else None,
                impact_level="medium"
            )
            db.add(event)
            events.append(event)

        db.commit()
        logger.info(f"Created {len(events)} timeline events")
        return events

    def _extract_keywords(self, items: List[Any]) -> Counter:
        """Extract keywords from items"""
        all_tags = []

        for item in items:
            tags = []
            if hasattr(item, 'tags') and item.tags:
                tags = item.tags if isinstance(item.tags, list) else []
            elif hasattr(item, 'metadata') and item.metadata and 'tags' in item.metadata:
                tags = item.metadata.get('tags', [])

            all_tags.extend(tags)

        return Counter(all_tags)

    def _create_trend_metrics(self, db: Session, keyword_counts: Counter) -> List[TrendMetric]:
        """Create trend metrics from keyword counts"""
        metrics = []
        today = date.today()

        for keyword, count in keyword_counts.items():
            tm = TrendMetric(
                metric_date=today,
                keyword=keyword,
                frequency=count,
                trend_direction="rising" if count >= 3 else "stable",
                score=count / len(keyword_counts) if keyword_counts else 0
            )
            db.add(tm)
            metrics.append(tm)

        db.commit()
        logger.info(f"Created {len(metrics)} trend metrics")
        return metrics
