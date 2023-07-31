from datetime import datetime
from app.core.schemas import BaseModel

class UserResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    displayname: str

class UserInput(BaseModel):
    displayname: str
