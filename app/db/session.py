from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
import logging
from app.core.config import settings


def get_sync_database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    return url


engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)

sync_engine = create_engine(get_sync_database_url(), future=True, echo=False)
SessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)


def get_session() -> Session:
    return SessionLocal()

#creates new AsyncSession objects .
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession, 
    autoflush=False, 
    autocommit=False, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def is_db_connected() -> bool:
  
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
        return False