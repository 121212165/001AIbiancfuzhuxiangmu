"""Frontier model - the exploration queue."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .node import Base


class Frontier(Base):
    """A seed for future exploration."""

    __tablename__ = "frontier"

    id = Column(Integer, primary_key=True, index=True)
    seed = Column(String(500), nullable=False, unique=True, index=True)
    priority = Column(Float, default=1.0, index=True)
    source_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "seed": self.seed,
            "priority": self.priority,
            "source_node_id": self.source_node_id,
            "attempts": self.attempts,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
