"""Edge model - relationships between nodes."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .node import Base


class Edge(Base):
    """A relationship between two nodes."""

    __tablename__ = "edges"

    from_node_id = Column(Integer, ForeignKey("nodes.id"), primary_key=True)
    to_node_id = Column(Integer, ForeignKey("nodes.id"), primary_key=True)
    relationship = Column(String(50), nullable=False)  # inspired_by/related_to/contradicts
    strength = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "relationship": self.relationship,
            "strength": self.strength,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
