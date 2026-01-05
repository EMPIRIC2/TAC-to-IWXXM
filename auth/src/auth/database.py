"""Database setup for authentication module (src layout)."""
from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/postgres"
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connection before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    from . import models  # noqa: F401 ensure models are imported
    Base.metadata.create_all(bind=engine)


__all__ = ["SessionLocal", "Base", "init_db"]
