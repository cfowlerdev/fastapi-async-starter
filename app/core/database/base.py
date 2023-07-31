from sqlalchemy import MetaData, inspect
from sqlalchemy.orm import declarative_base, declared_attr, Mapped, mapped_column

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

DeclarativeBase = declarative_base(
    metadata=MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)    
)

class BaseModel(DeclarativeBase):
    __abstract__ = True

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
        
    id: Mapped[int] = mapped_column(primary_key=True)
    
    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)
    
    def as_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
