from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from app.models import user as user_models
from app.schemas import user as user_schemas
from app.database import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

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