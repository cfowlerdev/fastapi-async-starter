from sqlalchemy import Column, String, BigInteger, SmallInteger
from sqlalchemy.orm import relationship

from app.core.database import mixins

class User(mixins.BaseModel, mixins.CRUDMixin):
    __tablename__ = "users"

    displayname = Column(String(255), nullable=True)
    