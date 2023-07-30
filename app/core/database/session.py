from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL), 
    pool_pre_ping=True,
    future=True,
    echo=settings.DATABASE_ECHO
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

