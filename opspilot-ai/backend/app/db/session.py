"""
Database engine and session setup.

Uses SQLite: zero setup, a single file at backend/data/opspilot.db. The
`connect_args` flag is SQLite-specific (allows the connection to be used
across FastAPI's threaded request handling); it's the only line that would
need to change if this were ever pointed at PostgreSQL instead.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
