import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


WRITE_DATABASE_URL = os.getenv("WRITE_DATABASE_URL", "sqlite:///write.db")
READ_DATABASE_URL = os.getenv("READ_DATABASE_URL", "sqlite:///read.db")

# Connection arguments (Fallback for SQLite)
connect_args = {"check_same_thread": False} if WRITE_DATABASE_URL.startswith("sqlite") else {}

# Create database engines
write_engine = create_engine(WRITE_DATABASE_URL, connect_args=connect_args)
read_engine = create_engine(READ_DATABASE_URL, connect_args=connect_args)

# Create session factories
SessionWrite = sessionmaker(autocommit=False, autoflush=False, bind=write_engine)
SessionRead = sessionmaker(autocommit=False, autoflush=False, bind=read_engine)

# Base model class
Base = declarative_base()

@contextmanager
def get_write_db() -> Generator:
    """Provides a transactional session for write operations."""
    db = SessionWrite()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Write transaction failed: {e}", exc_info=True)
        raise
    finally:
        db.close()

@contextmanager
def get_read_db() -> Generator:
    """Provides a session for read operations (read-only)."""
    db = SessionRead()
    try:
        yield db
    except Exception as e:
        logger.error(f"Read transaction failed: {e}", exc_info=True)
        raise
    finally:
        db.close()
