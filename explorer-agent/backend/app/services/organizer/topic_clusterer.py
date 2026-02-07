"""
Topic Clusterer for Organizer Agent
"""
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.knowledge import TopicCluster
from app.models.node import Node as ExplorationNode
from app.models.insight import Insight
import logging

logger = logging.getLogger(__name__)


class TopicClusterer:
    """
    Topic clusterer using embeddings, UMAP, and HDBSCAN

    Note: For v2.0 MVP, we're using a simplified tag-based clustering approach.
    Full implementation with sentence-transformers + UMAP + HDBSCAN can be added later.
    """

    def __init__(self):
        # For MVP, using simple tag-based clustering
        # Full implementation would use:
        # from sentence_transformers import SentenceTransformer
        # import umap
        # import hdbscan
        pass

    def cluster(self, items: List[Any]) -> Dict[str, Any]:
        """
        Cluster items by topic

        Args:
            items: List of nodes and insights

        Returns:
            {
                "clusters": List[Dict],
                "metrics": {...}
            }
        """
        if len(items) < 2:
            logger.warning("Not enough items to cluster")
            return {
                "clusters": [],
                "metrics": {"clusters_found": 0}
            }

        db = next(get_db())

        try:
            # For MVP: Simple tag-based clustering
            clusters_data = self._cluster_by_tags(db, items)

            return {
                "clusters": [
                    {
                        "id": tc.id,
                        "name": tc.cluster_name,
                        "description": tc.description,
                        "item_count": tc.item_count,
                        "confidence": tc.confidence
                    }
                    for tc in clusters_data
                ],
                "metrics": {
                    "clusters_found": len(clusters_data),
                    "noise_points": 0  # Tag-based clustering doesn't produce noise
                }
            }

        except Exception as e:
            logger.error(f"Failed to cluster topics: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()

    def _cluster_by_tags(self, db: Session, items: List[Any]) -> List[TopicCluster]:
        """Simple tag-based clustering for MVP"""
        # Collect all tags
        tag_to_items = {}

        for item in items:
            tags = []
            if hasattr(item, 'tags') and item.tags:
                tags = item.tags if isinstance(item.tags, list) else []
            elif hasattr(item, 'metadata') and item.metadata and 'tags' in item.metadata:
                tags = item.metadata.get('tags', [])

            for tag in tags:
                if tag not in tag_to_items:
                    tag_to_items[tag] = []
                tag_to_items[tag].append(item.id)

        # Create clusters from tags
        topic_clusters = []

        for tag, item_ids in tag_to_items.items():
            if len(item_ids) >= 1:  # Single-item clusters are ok for MVP
                tc = TopicCluster(
                    cluster_name=tag,
                    description=f"Items related to {tag}",
                    item_ids=item_ids,
                    item_count=len(item_ids),
                    confidence=0.8  # Fixed confidence for MVP
                )
                db.add(tc)
                topic_clusters.append(tc)

        db.commit()
        logger.info(f"Created {len(topic_clusters)} topic clusters")
        return topic_clusters
