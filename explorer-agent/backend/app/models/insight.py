"""Insight model - high-value insights extracted by Thinker."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Insight(Base):
    """A high-value insight extracted by Thinker from low-quality content."""

    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    source_node_ids = Column(JSON, nullable=False)  # IDs of source low-quality items
    insight_content = Column(Text, nullable=False)  # The extracted insight
    insight_type = Column(String(50), nullable=False, index=True)  # hidden_gem, synthesis, connection
    value_score = Column(Float, default=0.0, index=True)  # Re-evaluated score
    title = Column(Text, nullable=True)  # Optional title for the insight
    reasoning = Column(Text, nullable=True)  # Thinker's reasoning
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    meta_data = Column(JSON, default=dict)  # Additional data

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_node_ids": self.source_node_ids,
            "insight_content": self.insight_content,
            "insight_type": self.insight_type,
            "value_score": self.value_score,
            "title": self.title,
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "meta_data": self.meta_data or {},
        }
