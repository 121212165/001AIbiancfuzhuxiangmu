"""
Feedback Generator for Outputter Agent
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """
    Feedback generator

    Generates feedback for Explorer agent to optimize future explorations
    """

    def __init__(self):
        pass

    def generate_feedback(self, data: Dict[str, Any]) -> List[str]:
        """
        Generate feedback for Explorer

        Args:
            data: Organizer output data

        Returns:
            List[str]: List of feedback suggestions
        """
        feedback = []

        # 1. Topic-based feedback
        topics = data.get("topics", {}).get("clusters", [])
        if topics:
            top_topics = [t.get("name") for t in topics[:3]]
            if top_topics:
                feedback.append(f"Focus areas identified: {', '.join(top_topics)}")

        # 2. Trend-based feedback
        trends = data.get("trends", {})
        rising = trends.get("rising", [])
        if rising:
            feedback.append(f"Rising trends to explore deeper: {', '.join(rising[:3])}")

        # 3. Question-based feedback
        questions = data.get("questions", {}).get("questions", [])
        if questions:
            high_priority = [q for q in questions if q.get("importance") == "high"]
            if high_priority:
                feedback.append(f"High-priority research gaps: {len(high_priority)}")

        # 4. Graph structure feedback
        graph_metrics = data.get("knowledge_graph", {}).get("metrics", {})
        nodes_count = graph_metrics.get("nodes_count", 0)
        edges_count = graph_metrics.get("edges_count", 0)

        if nodes_count > 0 and edges_count == 0:
            feedback.append("Warning: Knowledge graph has no edges, consider exploring related topics")

        # 5. Generic feedback if none generated
        if not feedback:
            feedback.append("Continue exploration with current strategy")

        logger.info(f"Generated {len(feedback)} feedback items")
        return feedback
