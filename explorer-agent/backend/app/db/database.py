"""Database base configuration."""

from sqlalchemy.ext.declarative import declarative_base
from app.db.session import get_db

Base = declarative_base()

__all__ = ['Base', 'get_db']
