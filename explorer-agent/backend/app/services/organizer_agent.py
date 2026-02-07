"""
Organizer Agent - Knowledge Architect
"""
from typing import Dict, List, Any, Optional
from app.agents import AgentProtocol
from app.services.organizer.graph_builder import KnowledgeGraphBuilder
from app.services.organizer.topic_clusterer import TopicClusterer
from app.services.organizer.timeline_analyzer import TimelineAnalyzer
from app.services.organizer.question_discoverer import QuestionDiscoverer
import logging

logger = logging.getLogger(__name__)


class OrganizerAgent(AgentProtocol):
    """
    Organizer Agent - Knowledge Architect

    Responsibilities:
    1. Build knowledge graph
    2. Cluster topics
    3. Analyze timeline
    4. Identify trends
    5. Discover research questions
    """

    def __init__(self,
                 graph_builder: Optional[KnowledgeGraphBuilder] = None,
                 topic_clusterer: Optional[TopicClusterer] = None,
                 timeline_analyzer: Optional[TimelineAnalyzer] = None,
                 question_discoverer: Optional[QuestionDiscoverer] = None):
        """
        Initialize Organizer Agent

        Args:
            graph_builder: Knowledge graph builder
            topic_clusterer: Topic clusterer
            timeline_analyzer: Timeline analyzer
            question_discoverer: Question discoverer
        """
        self.graph_builder = graph_builder or KnowledgeGraphBuilder()
        self.topic_clusterer = topic_clusterer or TopicClusterer()
        self.timeline_analyzer = timeline_analyzer or TimelineAnalyzer()
        self.question_discoverer = question_discoverer or QuestionDiscoverer()

    def validate_input(self, input_data: Dict) -> bool:
        """Validate input data"""
        # At least high_quality or insights should be present
        has_high_quality = "high_quality" in input_data and input_data["high_quality"]
        has_insights = "insights" in input_data and input_data["insights"]

        if not has_high_quality and not has_insights:
            logger.error("Input validation failed: missing both 'high_quality' and 'insights'")
            return False

        return True

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute organization process

        Args:
            input_data: {
                "high_quality": List[Node],  # High-quality nodes
                "insights": List[Insight]    # Insights from Thinker
            }

        Returns:
            {
                "status": "success" | "partial" | "failed",
                "data": {
                    "knowledge_graph": {...},
                    "topics": {...},
                    "timeline": {...},
                    "trends": {...},
                    "questions": {...}
                },
                "metrics": {...},
                "errors": [...]
            }
        """
        import time
        start_time = time.time()

        errors = []

        # Validate input
        if not self.validate_input(input_data):
            return {
                "status": "failed",
                "data": None,
                "metrics": {},
                "errors": ["Input validation failed"]
            }

        high_quality = input_data.get("high_quality", [])
        insights = input_data.get("insights", [])

        try:
            # 1. Build knowledge graph
            logger.info("Step 1: Building knowledge graph...")
            graph_result = self.graph_builder.build(high_quality, insights)

            # 2. Cluster topics
            logger.info("Step 2: Clustering topics...")
            all_items = high_quality + insights
            topics_result = self.topic_clusterer.cluster(all_items)

            # 3. Analyze timeline
            logger.info("Step 3: Analyzing timeline...")
            timeline_result = self.timeline_analyzer.analyze(all_items)

            # 4. Identify trends
            logger.info("Step 4: Identifying trends...")
            trends_result = self.timeline_analyzer.identify_trends(all_items)

            # 5. Discover questions
            logger.info("Step 5: Discovering questions...")
            questions_result = self.question_discoverer.discover(
                graph_result.get("graph"),
                topics_result.get("clusters", [])
            )

            execution_time = time.time() - start_time

            return {
                "status": "success",
                "data": {
                    "knowledge_graph": graph_result,
                    "topics": topics_result,
                    "timeline": timeline_result,
                    "trends": trends_result,
                    "questions": questions_result
                },
                "metrics": {
                    "nodes_processed": len(all_items),
                    "graph_nodes": graph_result.get("metrics", {}).get("nodes_count", 0),
                    "graph_edges": graph_result.get("metrics", {}).get("edges_count", 0),
                    "topics_found": len(topics_result.get("clusters", [])),
                    "timeline_events": len(timeline_result.get("events", [])),
                    "trends_identified": len(trends_result.get("rising", [])),
                    "questions_found": len(questions_result.get("questions", [])),
                    "execution_time": round(execution_time, 2)
                },
                "errors": errors
            }

        except Exception as e:
            logger.error(f"Organizer agent failed: {str(e)}", exc_info=True)
            errors.append(str(e))

            return {
                "status": "failed",
                "data": None,
                "metrics": {"execution_time": round(time.time() - start_time, 2)},
                "errors": errors
            }

    def get_config(self) -> Dict:
        """Get configuration"""
        return {
            "agent_type": "OrganizerAgent",
            "components": {
                "graph_builder": self.graph_builder.__class__.__name__,
                "topic_clusterer": self.topic_clusterer.__class__.__name__,
                "timeline_analyzer": self.timeline_analyzer.__class__.__name__,
                "question_discoverer": self.question_discoverer.__class__.__name__
            }
        }
