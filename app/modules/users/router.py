import logging
from fastapi import APIRouter, Body, Depends, Query, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database.dependencies import async_dbsession
from app.modules.users.schemas import UserResponse, UserInput
from app.modules.users.models import User
from app.core.pagination.schemas import PagedResponse, PageParams
from app.core.auth.fake_auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    dependencies=[Depends(async_dbsession)]
)

@router.post(
    "/", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Creates a new user",
    tags=["User"],
    summary="Creates a new user"
)
async def create_user(
    input: UserInput = Body(),
    db: AsyncSession = Depends(async_dbsession),
    current_user: User = Depends(get_current_user) 
):
    try:
        user = await User.async_add_by_schema(db, input)
    except Exception as e:
        logger.error(f"Unable to create new user : {str(e)}")
        raise HTTPException(status_code=400, detail="Creation error")
    else:
        return user

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description="Get a user by ID",
    tags=["User"],
    summary="Get a user by ID"    
)
async def get_user(
    user_id: int, db: AsyncSession = Depends(async_dbsession), 
    current_user: User = Depends(get_current_user)
):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Item not found")
    return UserResponse.model_validate(user)
    
@router.get(
    "/",
    response_model=PagedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    description="Get list of users based on filter",
    tags=["User"],
    summary="Get list of users"    
)
async def get_users(
    page_params: PageParams = Depends(), 
    db: AsyncSession = Depends(async_dbsession), 
    current_user: User = Depends(get_current_user)
):
    rows, total_count = await User.filter(db=db, offset=(page_params.page - 1) * page_params.size, count=True)
    return PagedResponse(
        total = total_count,
        page = page_params.page,
        size = page_params.size,
        results = [UserResponse.model_validate(item) for item in rows]
    )

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    description="Update a user by ID",
    tags=["User"],
    summary="Update a user by ID"    
)
async def update_user(
    user_id: int, 
    input: UserInput = Body(), 
    db: AsyncSession = Depends(async_dbsession), 
    current_user: User = Depends(get_current_user)
):
    user = await User.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Item not found")
    await user.update(db, id=user_id, **input.model_dump(), )
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a user by ID",
    tags=["User"],
    summary="Delete a user by ID"    
)
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(async_dbsession), 
    current_user: User = Depends(get_current_user)
):
    result = await User.delete(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return