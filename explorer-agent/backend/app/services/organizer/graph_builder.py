"""
Knowledge Graph Builder for Organizer Agent
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.knowledge import KnowledgeNode, KnowledgeEdge
from app.models.node import Node as ExplorationNode
from app.models.insight import Insight
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """
    Knowledge graph builder

    Creates nodes and edges from exploration results and insights
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def build(self,
              high_quality_nodes: List[ExplorationNode],
              insights: List[Insight]) -> Dict[str, Any]:
        """
        Build knowledge graph from nodes and insights

        Args:
            high_quality_nodes: List of high-quality exploration nodes
            insights: List of insights from Thinker agent

        Returns:
            {
                "graph": nx.Graph,
                "nodes": List[KnowledgeNode],
                "edges": List[KnowledgeEdge],
                "metrics": {...}
            }
        """
        db = next(get_db())

        try:
            # 1. Create knowledge nodes
            knowledge_nodes = self._create_nodes(db, high_quality_nodes, insights)

            # 2. Create knowledge edges
            knowledge_edges = self._create_edges(db, knowledge_nodes)

            # 3. Build NetworkX graph
            graph = self._build_networkx_graph(knowledge_nodes, knowledge_edges)

            # 4. Compute graph metrics
            metrics = self._compute_graph_metrics(graph)

            logger.info(f"Built knowledge graph: {metrics['nodes_count']} nodes, {metrics['edges_count']} edges")

            return {
                "graph": graph,
                "nodes": knowledge_nodes,
                "edges": knowledge_edges,
                "metrics": metrics
            }

        except Exception as e:
            logger.error(f"Failed to build knowledge graph: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()

    def _create_nodes(self,
                     db: Session,
                     high_quality_nodes: List[ExplorationNode],
                     insights: List[Insight]) -> List[KnowledgeNode]:
        """Create knowledge graph nodes from exploration nodes and insights"""
        knowledge_nodes = []

        # Create nodes from high-quality exploration nodes
        for node in high_quality_nodes:
            kn = KnowledgeNode(
                node_type="paper",
                title=node.title,
                description=node.content[:500] if node.content and len(node.content) > 500 else node.content,
                metadata={
                    "source": node.source,
                    "url": node.url,
                    "value_score": node.value_score,
                    "tags": node.tags or []
                },
                source_node_id=node.id,
                source_type="node"
            )
            db.add(kn)
            knowledge_nodes.append(kn)

        # Create nodes from insights
        for insight in insights:
            kn = KnowledgeNode(
                node_type="insight",
                title=insight.title or f"Insight from {len(insight.source_node_ids or [])} sources",
                description=insight.insight_content,
                metadata={
                    "insight_type": insight.insight_type,
                    "related_nodes": insight.source_node_ids or [],
                    "confidence": insight.value_score
                },
                source_node_id=insight.id,
                source_type="insight"
            )
            db.add(kn)
            knowledge_nodes.append(kn)

        db.commit()
        logger.info(f"Created {len(knowledge_nodes)} knowledge nodes")
        return knowledge_nodes

    def _create_edges(self,
                     db: Session,
                     knowledge_nodes: List[KnowledgeNode]) -> List[KnowledgeEdge]:
        """Create edges between knowledge nodes based on similarity"""
        edges = []

        # Simple strategy: create edges based on tag similarity
        for i, node1 in enumerate(knowledge_nodes):
            for node2 in knowledge_nodes[i+1:]:
                similarity = self._compute_similarity(node1, node2)

                if similarity > 0.3:  # Similarity threshold
                    edge = KnowledgeEdge(
                        source_id=node1.id,
                        target_id=node2.id,
                        edge_type="related_to",
                        weight=similarity,
                        metadata={"similarity": similarity}
                    )
                    db.add(edge)
                    edges.append(edge)

        db.commit()
        logger.info(f"Created {len(edges)} knowledge edges")
        return edges

    def _compute_similarity(self,
                          node1: KnowledgeNode,
                          node2: KnowledgeNode) -> float:
        """Compute similarity between two nodes"""
        # Simple implementation based on tag overlap
        tags1 = set()
        tags2 = set()

        if node1.metadata and "tags" in node1.metadata:
            tags1 = set(node1.metadata["tags"] or [])
        if node2.metadata and "tags" in node2.metadata:
            tags2 = set(node2.metadata["tags"] or [])

        if not tags1 or not tags2:
            return 0.0

        intersection = len(tags1 & tags2)
        union = len(tags1 | tags2)

        return intersection / union if union > 0 else 0.0

    def _build_networkx_graph(self,
                             nodes: List[KnowledgeNode],
                             edges: List[KnowledgeEdge]) -> nx.DiGraph:
        """Build NetworkX graph from nodes and edges"""
        graph = nx.DiGraph()

        # Add nodes
        for node in nodes:
            graph.add_node(
                node.id,
                node_type=node.node_type,
                title=node.title,
                description=node.description
            )

        # Add edges
        for edge in edges:
            graph.add_edge(
                edge.source_id,
                edge.target_id,
                edge_type=edge.edge_type,
                weight=edge.weight
            )

        return graph

    def _compute_graph_metrics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Compute graph metrics"""
        return {
            "nodes_count": graph.number_of_nodes(),
            "edges_count": graph.number_of_edges(),
            "density": round(nx.density(graph), 4),
            "is_connected": nx.is_weakly_connected(graph)
        }
