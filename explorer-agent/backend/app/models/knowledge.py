"""
Knowledge models for Organizer Agent
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Date, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base


class KnowledgeNode(Base):
    """Knowledge graph node"""
    __tablename__ = "knowledge_nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_type = Column(String(50), nullable=False, comment="paper, concept, author, insight, method, dataset")
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    meta_data = Column(JSONB, nullable=True)
    source_node_id = Column(Integer, nullable=True, comment="Reference to original node or insight")
    source_type = Column(String(50), nullable=True, comment="node or insight")
    embedding = Column(ARRAY(Float), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<KnowledgeNode(id={self.id}, type='{self.node_type}', title='{self.title}')>"


class KnowledgeEdge(Base):
    """Knowledge graph edge"""
    __tablename__ = "knowledge_edges"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, comment="knowledge_nodes.id")
    target_id = Column(Integer, nullable=False, comment="knowledge_nodes.id")
    edge_type = Column(String(50), nullable=False, comment="cites, discusses, uses, applies_to, related_to, etc.")
    weight = Column(Float, nullable=True, default=1.0)
    meta_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    def __repr__(self):
        return f"<KnowledgeEdge(id={self.id}, {self.source_id} -> {self.target_id}, type='{self.edge_type}')>"


class TopicCluster(Base):
    """Topic cluster"""
    __tablename__ = "topic_clusters"

    id = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    item_ids = Column(ARRAY(Integer), nullable=True, comment="Node and insight IDs in this cluster")
    cluster_center = Column(ARRAY(Float), nullable=True, comment="Cluster center vector")
    item_count = Column(Integer, nullable=True, default=0)
    confidence = Column(Float, nullable=True, comment="Cluster confidence score")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    def __repr__(self):
        return f"<TopicCluster(id={self.id}, name='{self.cluster_name}', items={self.item_count})>"


class TimelineEvent(Base):
    """Timeline event"""
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(Date, nullable=False)
    event_type = Column(String(50), nullable=True, comment="breakthrough, publication, trend_change")
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    related_node_ids = Column(ARRAY(Integer), nullable=True)
    impact_level = Column(String(20), nullable=True, comment="high, medium, low")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    def __repr__(self):
        return f"<TimelineEvent(id={self.id}, date='{self.event_date}', type='{self.event_type}')>"


class TrendMetric(Base):
    """Trend metric"""
    __tablename__ = "trend_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(Date, nullable=False)
    keyword = Column(String(100), nullable=False)
    frequency = Column(Integer, nullable=True, default=0)
    trend_direction = Column(String(20), nullable=True, comment="rising, stable, declining")
    score = Column(Float, nullable=True, comment="Trend score")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    def __repr__(self):
        return f"<TrendMetric(id={self.id}, keyword='{self.keyword}', direction='{self.trend_direction}')>"


class ResearchQuestion(Base):
    """Research question"""
    __tablename__ = "research_questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=True, comment="gap, contradiction, opportunity")
    context = Column(JSONB, nullable=True)
    importance = Column(String(20), nullable=True, comment="high, medium, low")
    suggested_exploration = Column(String(500), nullable=True)
    status = Column(String(20), nullable=True, default="open", comment="open, answered")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    def __repr__(self):
        return f"<ResearchQuestion(id={self.id}, status='{self.status}', importance='{self.importance}')>"
