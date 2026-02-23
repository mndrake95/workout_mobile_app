from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import config
from app.models import user as user_models
from app.database import get_db
from app.services.auth import decode_and_validate_token
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    payload = decode_and_validate_token(token, config.settings.SECRET_KEY, [config.settings.ALGORITHM])
    username = payload.get("sub")
    if not username: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    query = select(user_models.User).where(user_models.User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user

async def get_current_user_optional(token: Annotated[Optional[str], Depends(optional_oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    if token is None: 
        return None
    try:
        payload = decode_and_validate_token(token, config.settings.SECRET_KEY, [config.settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        query = select(user_models.User).where(user_models.User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")