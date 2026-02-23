from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.dependencies import get_current_user, get_current_user_optional
from app.models import user as user_models
from app.models import exercise as exercise_models
from app.schemas import exercise as exercise_schemas
from app.database import get_db
from math import ceil

router = APIRouter()

@router.post("/exercises", 
             tags=["exercises"], 
             status_code=status.HTTP_201_CREATED,
             response_model=exercise_schemas.ExerciseResponse)
async def create_exercise(exercise: exercise_schemas.ExerciseCreate, 
                          current_user: user_models.User = Depends(get_current_user), 
                          db: AsyncSession = Depends(get_db)):
    new_exercise = exercise_models.Exercise(title = exercise.title,
                                            type = exercise.type,
                                            body_parts = exercise.body_parts,
                                            author = current_user.id
                                            )
    db.add(new_exercise)
    await db.commit()
    await db.refresh(new_exercise)
    return new_exercise

@router.get("/exercises",
            tags=["exercises"],
            status_code=status.HTTP_200_OK,
            response_model=exercise_schemas.ExerciseListResponse)
async def get_list_of_exercises(body_parts: Optional[str] = None,
                                type: Optional[str] = None,
                                page: int = 1,
                                limit: int = 10,
                                db: AsyncSession = Depends(get_db)
                                ):
    base_query = select(exercise_models.Exercise)

    if body_parts is not None:
        base_query = base_query.where(exercise_models.Exercise.body_parts == body_parts)
    
    if type is not None:
        base_query = base_query.where(exercise_models.Exercise.type == type)

    count_query = select(func.count()).select_from(base_query.subquery())
    count = await db.scalar(count_query)

    page_query = base_query.order_by(exercise_models.Exercise.id).offset((page - 1) * limit).limit(limit)
    result = await db.execute(page_query)
    page_result = result.scalars().all()

    total_pages = ceil(count / limit)

    return {
            "items": page_result,
            "total": count,
            "page": page,
            "pages": total_pages,
        }
    
