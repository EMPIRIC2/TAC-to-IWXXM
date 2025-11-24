"""Database setup for authentication module."""
from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("AUTH_DB_URL", "sqlite:///./auth.db")

class Base(DeclarativeBase):
    pass

# SQLite needs check_same_thread=False for multi-threaded FastAPI usage
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    from . import models  # noqa: F401 ensure models are imported
    Base.metadata.create_all(bind=engine)

__all__ = ["SessionLocal", "Base", "init_db"]
