from sqlalchemy import Column, String

from app.core.database import mixins, base

class User(base.BaseModel, mixins.WithTimestamps, mixins.WithAsyncCrud):
    __tablename__ = "users"

    displayname = Column(String(255), nullable=True)
    