from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @model_validator(mode="after")
    def check_identifier(cls, values):
        if not (values.username or values.email):
            raise ValueError("Either username or email must be provided for login")
        return values


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

