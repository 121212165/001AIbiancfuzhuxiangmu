"""LowQualityPool model - temporary storage for low-quality content."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LowQualityPool(Base):
    """A temporary storage for low-quality content awaiting Thinker processing."""

    __tablename__ = "low_quality_pool"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    source = Column(String(500), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False)  # article/paper/video/idea
    original_score = Column(Float, nullable=False, index=True)  # Evaluator's original score
    tags = Column(JSON, default=list)  # Tags from evaluator
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    processed = Column(Boolean, default=False, index=True)  # Whether Thinker has processed this
    processing_attempts = Column(Integer, default=0)  # How many times Thinker tried

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "source": self.source,
            "type": self.type,
            "original_score": self.original_score,
            "tags": self.tags or [],
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
            "processed": self.processed,
            "processing_attempts": self.processing_attempts,
        }
