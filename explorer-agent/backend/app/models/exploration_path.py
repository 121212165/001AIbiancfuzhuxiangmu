"""ExplorationPath model - tracks discovery chains."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ARRAY, Text
from sqlalchemy.orm import relationship
from .node import Base


class ExplorationPath(Base):
    """An exploration path - A → B → C discovery chain."""

    __tablename__ = "exploration_paths"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(ARRAY(Integer), nullable=False)  # [node_id_1, node_id_2, ...]
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    total_value = Column(Float, default=0.0)
    strategy = Column(String(50), nullable=False)  # random/edge/graph

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "path": self.path,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_value": self.total_value,
            "strategy": self.strategy,
            "nodes_count": len(self.path) if self.path else 0,
        }
