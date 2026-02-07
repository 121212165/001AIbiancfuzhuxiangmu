"""
Question Discoverer for Organizer Agent
"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.knowledge import ResearchQuestion
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class QuestionDiscoverer:
    """
    Question discoverer

    Identifies research gaps, contradictions, and opportunities
    """

    def __init__(self):
        pass

    def discover(self,
                graph: nx.DiGraph,
                clusters: List[Any]) -> Dict[str, Any]:
        """
        Discover research questions

        Args:
            graph: Knowledge graph
            clusters: Topic clusters

        Returns:
            {
                "questions": List[Dict],
                "metrics": {...}
            }
        """
        db = next(get_db())

        try:
            questions = []

            # For MVP: Generate simple questions based on graph structure
            if graph and graph.number_of_nodes() > 0:
                questions.extend(self._discover_graph_questions(db, graph))

            # Generate questions based on clusters
            if clusters:
                questions.extend(self._discover_cluster_questions(db, clusters))

            return {
                "questions": [
                    {
                        "id": q.id,
                        "question": q.question,
                        "type": q.question_type,
                        "importance": q.importance,
                        "suggested_exploration": q.suggested_exploration
                    }
                    for q in questions
                ],
                "metrics": {
                    "questions_found": len(questions)
                }
            }

        except Exception as e:
            logger.error(f"Failed to discover questions: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()

    def _discover_graph_questions(self, db: Session, graph: nx.DiGraph) -> List[ResearchQuestion]:
        """Discover questions based on graph structure"""
        questions = []

        # Find isolated nodes (potential gaps)
        if nx.is_weakly_connected(graph):
            # Graph is connected, look for low-degree nodes instead
            degrees = dict(graph.degree())
            low_degree_nodes = [node for node, degree in degrees.items() if degree <= 1]

            if low_degree_nodes:
                q = ResearchQuestion(
                    question=f"Why do {len(low_degree_nodes)} nodes have few connections? Are there missing relationships?",
                    question_type="gap",
                    importance="medium",
                    suggested_exploration=f"Explore connections for isolated nodes: {low_degree_nodes[:3]}"
                )
                db.add(q)
                questions.append(q)

        return questions

    def _discover_cluster_questions(self, db: Session, clusters: List[Any]) -> List[ResearchQuestion]:
        """Discover questions based on topic clusters"""
        questions = []

        # Look for small clusters (potential niches)
        if clusters:
            small_clusters = [c for c in clusters if c.item_count and c.item_count <= 2]

            if small_clusters:
                for cluster in small_clusters[:3]:  # Limit to 3
                    q = ResearchQuestion(
                        question=f"Is '{cluster.cluster_name}' an emerging topic with few publications?",
                        question_type="opportunity",
                        importance="low",
                        suggested_exploration=f"Deep dive into: {cluster.cluster_name}"
                    )
                    db.add(q)
                    questions.append(q)

        return questions
