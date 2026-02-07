"""Initialize database with pgvector extension and tables."""

from sqlalchemy import text
from app.db.session import engine
from app.models.node import Base
# Import all models to register them with Base
from app.models import Node, ExplorationPath, Frontier, Edge


def init_db():
    """Initialize database."""
    # Enable pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
