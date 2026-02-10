from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    author: int

    model_config = {'from_attributes': True}