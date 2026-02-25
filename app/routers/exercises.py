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
from datetime import datetime

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
                                current_user: user_models.User = Depends(get_current_user_optional),
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

    items = []
    for exercise in page_result:
        is_mine = current_user is not None and exercise.author == current_user.id
        items.append({
            "id": exercise.id,
            "title": exercise.title,
            "type": exercise.type,
            "body_parts": exercise.body_parts,
            "is_mine": is_mine,
            "created_at": exercise.created_at,
            "author": exercise.author
        })

    return {
            "items": items,
            "total": count,
            "page": page,
            "pages": total_pages,
        } 

@router.get("/exercises/{exercise_id}",
            tags=["exercises"],
            status_code=status.HTTP_200_OK,
            response_model=exercise_schemas.ExerciseResponse)
async def get_exercise_by_id(exercise_id: int, db: AsyncSession = Depends(get_db)):
    query = select(exercise_models.Exercise)
    query = query.where(exercise_models.Exercise.id == exercise_id)

    result = await db.execute(query)
    id_result = result.scalar_one_or_none()

    if id_result is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise does not exist")
    
    return id_result

@router.patch("/exercises/{exercise_id}",
              tags=["exercises"],
              status_code=status.HTTP_200_OK,
              response_model=exercise_schemas.ExerciseResponse)
async def patch_exercise_by_id(updated_exercise: exercise_schemas.ExerciseUpdate,
                               exercise_id: int,
                               current_user: user_models.User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db),
                               ):
    query = select(exercise_models.Exercise)
    query = query.where(exercise_models.Exercise.id == exercise_id)

    result = await db.execute(query)
    current_exercise = result.scalar_one_or_none()

    if current_exercise is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise does not exist")
 
    if current_user.id != current_exercise.author:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    if updated_exercise.title is not None:
        current_exercise.title = updated_exercise.title
    if updated_exercise.type is not None:
        current_exercise.type = updated_exercise.type
    if updated_exercise.body_parts is not None: 
        current_exercise.body_parts = updated_exercise.body_parts

    db.add(current_exercise)
    await db.commit()
    await db.refresh(current_exercise)

    return current_exercise

@router.delete("/exercises/{exercise_id}",
              tags=["exercises"],
              status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise_by_id(exercise_id: int,
                                current_user: user_models.User = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db),
                                ):
    query = select(exercise_models.Exercise)
    query = query.where(exercise_models.Exercise.id == exercise_id)

    result = await db.execute(query)
    current_exercise = result.scalar_one_or_none()

    if current_exercise is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise does not exist")
 
    if current_user.id != current_exercise.author:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    await db.delete(current_exercise)
    await db.commit()
