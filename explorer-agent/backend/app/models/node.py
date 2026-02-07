"""Node model - represents a piece of discovered content."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ARRAY, Text
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Node(Base):
    """A knowledge node - a piece of discovered content."""

    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    source = Column(String(500), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # article/paper/video/idea
    embedding = Column(Vector(1536), nullable=True)  # Semantic embedding
    value_score = Column(Float, default=0.0, index=True)
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    tags = Column(ARRAY(String), default=list)
    meta_data = Column(Text, nullable=True)  # JSON string for additional data

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "source": self.source,
            "type": self.type,
            "value_score": self.value_score,
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
            "tags": self.tags or [],
        }
