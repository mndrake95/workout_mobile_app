from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ExerciseBase(BaseModel):
    title: str
    type: str
    body_parts: str

class ExerciseCreate(ExerciseBase):
    pass    

class ExerciseUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    body_parts: Optional[str] = None

class ExerciseResponse(ExerciseBase):
    id: int
    created_at: datetime
    author: Optional[int]
    is_mine: bool = False

    model_config = {'from_attributes': True}

class ExerciseListResponse(BaseModel):
    items: List[ExerciseResponse]
    total: int
    page: int
    pages: int