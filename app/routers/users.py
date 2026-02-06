from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models import user as user_models
from app.schemas import user as user_schemas
from app.database import get_db
from app.services.auth import create_access_token, verify_and_update_password, pwd_context

router = APIRouter()

@router.post("/users/register", tags=["users"], status_code = status.HTTP_201_CREATED, response_model = user_schemas.UserResponse)
async def create_user(user: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_pw = pwd_context.hash(user.password)
    new_user = user_models.User(username = user.username,
                           email = user.email,
                           password_hash = hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/users/login", tags=["users"], status_code = status.HTTP_200_OK, response_model = user_schemas.TokenResponse)
async def login_user(login_data: user_schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(user_models.User).where(
        or_(
            user_models.User.username == login_data.username,
            user_models.User.email == login_data.email
        )
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_and_update_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.username)})  
    
    return {"access_token": access_token, "token_type": "bearer"}