from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
from app.logging_config import logger
from typing import AsyncGenerator

# Configure the asynchronous database engine
engine = create_async_engine(
    settings.database_url,
    future=True,
    echo=False
)

# Async session maker
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for yielding database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

async def init_db():
    """Initializes tables in the SQLite database"""
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        # Import models to register them on Base metadata before creation
        from app.models.session import ConversationalSession, SessionMessage
        from app.models.campaign import Campaign, CampaignItem
        
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialization complete.")
