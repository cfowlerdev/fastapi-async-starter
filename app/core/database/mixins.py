import logging
from datetime import datetime
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import Mapped, mapped_column, selectinload, exc
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class WithTimestamps(object):
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now())

class WithAsyncCrud(object):
    __table__args__ = {"extend_existing": True}

    async def commit(self, db: AsyncSession):
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc
    
    @classmethod
    async def create(cls, db: AsyncSession, instance: "WithAsyncCrud") -> "WithAsyncCrud":
        db.add(instance)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc
        else:
            try:
                await db.refresh(instance)
            except Exception:
                return instance
            return instance
        

    @classmethod
    async def create_from_schema(cls, db: AsyncSession, instance_schema):
        instance = cls(**instance_schema.dict())
        return await cls.create(db, instance)
    
    @classmethod
    async def create_from_kwargs(cls, db: AsyncSession, **kwargs):
        instance = cls(**kwargs)
        return await cls.add(db, instance)
    
    @classmethod
    async def get_by_id(cls, db: AsyncSession, id):
        try:
            result = await db.get(cls, id)
            return result
        except exc.NoResultFound:
            return None

    @classmethod
    async def filter(cls, db: AsyncSession, where=None, select_in_load=None, order_by=None, limit=None, offset=None, for_update=False, count=False):
        stmt = select(cls, for_update)
        
        if where is not None:
            stmt = stmt.where(where)
        if select_in_load is not None:
            stmt = stmt.options(selectinload(select_in_load))
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        # Execute the main query and fetch the results
        result = await db.execute(stmt)
        rows = result.scalars().all()
        await db.flush()

        # Create a separate count query to get the total count
        total_count = None        
        if count:
            count_stmt = select(func.count()).select_from(cls)
            if where is not None:
                count_stmt = count_stmt.where(where)
            count_result = await db.execute(count_stmt)
            total_count = count_result.scalar()
            
        return rows, total_count

    @classmethod
    async def find_first(cls, db: AsyncSession, where=None, select_in_load=None, order_by=None, for_update=False):
        stmt = select(cls, for_update)
        
        if where is not None:
            stmt = stmt.where(where)
        if select_in_load is not None:
            stmt = stmt.options(selectinload(select_in_load))
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt.limit = 1
        # Execute the main query and fetch the results
        result = await db.execute(stmt)
        row = result.scalars().first()
        await db.flush()

        return row

    @classmethod
    async def update(cls, db: AsyncSession, id, **kwargs):
        await db.execute(update(cls).where(cls.id == id).values(kwargs))
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc
        else:
            await db.flush()
        
    @classmethod
    async def delete(cls, db: AsyncSession, id) -> bool:
        result = await db.execute(delete(cls).where(cls.id == id))
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc
        else:
            await db.flush()
        return result.rowcount > 0
        
