from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.session import AsyncSessionLocal

async def async_dbsession() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
