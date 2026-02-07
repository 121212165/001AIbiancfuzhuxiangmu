"""
Outputter models for Outputter Agent
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base


class GeneratedReport(Base):
    """Generated report"""
    __tablename__ = "generated_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50), nullable=False, comment="daily, weekly, insight_brief")
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    format = Column(String(20), nullable=True, default="markdown", comment="markdown, html, json")
    meta_data = Column(JSONB, nullable=True)
    file_path = Column(String(500), nullable=True, comment="Generated file path")
    feedback_to_explorer = Column(JSONB, nullable=True, comment="Suggestions for exploration optimization")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    def __repr__(self):
        return f"<GeneratedReport(id={self.id}, type='{self.report_type}', title='{self.title}')>"
