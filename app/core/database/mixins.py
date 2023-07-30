import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    inspect,
    Boolean,
    select,
    delete,
)
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, declared_attr, selectinload, declarative_base

DeclarativeBase = declarative_base()

class BaseModel(DeclarativeBase):
    __abstract__ = True

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
        
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=False), nullable=False, default=datetime.datetime.now)
    updated_at = Column(DateTime(timezone=False), nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)
    
    def as_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    
class CRUDMixin(object):

    __table_args__ = {"extend_existing": True}

    async def commit(self, db: AsyncSession):
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc

    @classmethod
    async def _async_filter(
        cls,
        db: AsyncSession,
        where,
        select_in_load,
        order_by,
        limit,
        for_update,
    ) -> ScalarResult:
        """
        Creating a select request with filter and restrictions

        :param db: Database session
        :param where: An expression for where
        :param select_in_load: Load related objects by key (eager loade)
        :param order_by: Grouping by field
        :param limit: Limiting the number of records
        """
        expression = select(cls, for_update)
        if where is not None:
            expression = expression.where(where)
        if select_in_load is not None:
            expression = expression.options(selectinload(select_in_load))
        if order_by is not None:
            expression = expression.order_by(order_by)
        if limit is not None:
            expression = expression.limit(limit)
        result = await db.execute(expression)
        return result.scalars()

    @classmethod
    async def async_delete(
        cls,
        db: AsyncSession,
        where,
    ) -> bool:
        """
        Removing objects

        :param db: Database session
        :param where: An expression for where
        """
        expression = delete(cls)
        if where is not None:
            expression = expression.where(where)

        result = await db.execute(expression)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            raise exc
        else:
            await db.flush()
        return result.rowcount > 0

    @classmethod
    async def async_filter(
        cls,
        db: AsyncSession,
        where=None,
        select_in_load=None,
        order_by=None,
        limit=None,
        for_update=False,
    ):
        scalars = await cls._async_filter(
            db,
            where,
            select_in_load,
            order_by=order_by,
            limit=limit,
            for_update=for_update,
        )
        result = scalars.all()
        await db.flush()
        return result

    @classmethod
    async def async_first(
        cls,
        db: AsyncSession,
        where=None,
        select_in_load=None,
        order_by=None,
        for_update=False,
    ) -> "CRUDMixin":
        scalars = await cls._async_filter(
            db,
            where,
            select_in_load,
            order_by=order_by,
            limit=1,
            for_update=for_update,
        )
        result = scalars.first()
        await db.flush()
        return result

    @classmethod
    async def async_all(cls, db: AsyncSession):
        """
        Async get all objects

        :return: list[EntityModelClass]
        """
        result = await db.execute(select(cls))
        res = result.scalars().all()
        await db.flush()
        return res

    @classmethod
    async def async_add(
        cls,
        db: AsyncSession,
        instance: "CRUDMixin",
    ) -> "CRUDMixin":
        """
        Async Create/Update by instance
        """
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
    async def async_add_by_kwargs(cls, db: AsyncSession, **kwargs):
        """
        Async Create/Update by kwargs
        """
        instance = cls(**kwargs)
        return await cls.async_add(db, instance)

    @classmethod
    async def async_add_by_schema(cls, db: AsyncSession, instance_schema):
        """
        Async create/update by instance_schema

        :param db: Db db
        :param instance_schema: Pydantic schema
        """
        instance = cls(**instance_schema.dict())
        return await cls.async_add(db, instance)

    @classmethod
    def all(cls, db: Session):
        return db.query(cls).filter().all()

    @classmethod
    def sync_add(cls, db: Session, instance):
        db.add(instance)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise exc
        else:
            return instance

    @classmethod
    def sync_add_by_schema(cls, db: Session, instance_schema):
        instance = cls(**instance_schema.dict())
        return cls.sync_add(db, instance)

    @classmethod
    def first(cls, db: Session, **kwargs):
        return db.query(cls).filter_by(**kwargs).first()

    @classmethod
    def filter_by(cls, db: Session, **kwargs):
        return db.query(cls).filter_by(**kwargs).all()
    