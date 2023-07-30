import logging
from fastapi import APIRouter, Body, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.dependencies import async_dbsession
from app.modules.users.schemas import UserResponse, UserInput
from app.modules.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    input: UserInput = Body(),
    db: AsyncSession = Depends(async_dbsession)   
):
    try:
        user = await User.async_add_by_schema(db, input)
    except Exception as e:
        logger.error(f"Unable to create new user : {str(e)}")
        raise HTTPException(status_code=400, detail="Creation error")
    else:
        return user
    