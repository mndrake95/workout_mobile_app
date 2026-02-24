from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import Optional
from app.dependencies import get_current_user, get_current_user_optional
from app.models import user as user_models
from app.models import exercise as exercise_models
from app.schemas import exercise as exercise_schemas
from app.database import get_db
from math import ceil

router = APIRouter()

