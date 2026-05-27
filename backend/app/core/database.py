"""SQLAlchemy async engine and session factory with startup checks."""
import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.async_database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> dict:
    """
    Verify PostgreSQL connectivity and check PostGIS + pgvector extensions.
    Returns status dict. Logs errors if connection or extensions are missing.
    """
    status = {"postgres": "ok", "postgis": "ok", "pgvector": "ok"}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        status["postgres"] = "unavailable"
        status["postgis"] = "unknown"
        status["pgvector"] = "unknown"
        return status

    # Check PostGIS
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'postgis'")
            )
            if not result.fetchone():
                logger.error("PostGIS extension is not enabled on the connected database.")
                status["postgis"] = "missing"
    except Exception as e:
        logger.error(f"PostGIS check failed: {e}")
        status["postgis"] = "error"

    # Check pgvector
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            if not result.fetchone():
                logger.error("pgvector extension (vector) is not enabled on the connected database.")
                status["pgvector"] = "missing"
    except Exception as e:
        logger.error(f"pgvector check failed: {e}")
        status["pgvector"] = "error"

    return status
