from datetime import datetime
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    displayname: str

    class Config:
        orm_mode = True

class UserInput(BaseModel):
    displayname: str
