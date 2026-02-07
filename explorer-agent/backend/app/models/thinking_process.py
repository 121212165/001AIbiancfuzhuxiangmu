"""ThinkingProcess model - tracks Thinker's processing sessions."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ThinkingProcess(Base):
    """A record of a Thinker processing session."""

    __tablename__ = "thinking_processes"

    id = Column(Integer, primary_key=True, index=True)
    session_type = Column(String(50), nullable=False)  # mine_gems, synthesize, discover_connections
    input_low_quality_ids = Column(JSON, nullable=False)  # IDs of processed items
    thinking_prompt = Column(Text, nullable=True)  # The prompt used
    thinking_result = Column(Text, nullable=True)  # AI's raw thinking output
    extracted_insights = Column(JSON, default=list)  # List of insight IDs created
    new_frontier_seeds = Column(JSON, default=list)  # New seeds added to frontier
    processing_time = Column(Float, default=0.0)  # Time taken in seconds
    ai_model_used = Column(String(100), nullable=True)  # Which AI model was used
    status = Column(String(20), default="completed")  # completed, failed, partial
    error_message = Column(Text, nullable=True)  # Error if failed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "session_type": self.session_type,
            "input_low_quality_ids": self.input_low_quality_ids,
            "thinking_prompt": self.thinking_prompt,
            "thinking_result": self.thinking_result,
            "extracted_insights": self.extracted_insights or [],
            "new_frontier_seeds": self.new_frontier_seeds or [],
            "processing_time": self.processing_time,
            "ai_model_used": self.ai_model_used,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
