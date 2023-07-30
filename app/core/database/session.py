from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

async_engine = create_async_engine(
    str(settings.DATABASE_URL), 
    pool_pre_ping=True,
    future=True,
    echo=settings.DATABASE_ECHO
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

