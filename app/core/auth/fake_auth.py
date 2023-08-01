import logging
from typing import Annotated
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.database.dependencies import async_dbsession
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import settings
from app.modules.users.models import User

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(
    dependencies=[Depends(async_dbsession)]
)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    displayname: str

def verify_password(plain_password:str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return encoded_jwt

# Dependency for use in routes to get current user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(async_dbsession)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(displayname=username)
    except JWTError:
        raise credentials_exception

    user = await User.find_first(db=db, where=User.displayname == token_data.displayname)
    if user is None:
        raise credentials_exception
    return user

# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    user = await User.find_first(db=db, where=User.displayname == username)
    # WARNING : DO NOT PUT IN PRODUCTION. THIS IS FOR DEV/TEST ONLY
    # Fake auth where password = displayname
    hashed_password = get_password_hash(username)
    if not user:
        return None
    if not verify_password(password, hashed_password):
        return None
    return user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),  db: AsyncSession = Depends(async_dbsession)):
    user = await authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes = settings.JWT_EXP)
    access_token = create_access_token(
        data = {"sub": user.displayname}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")