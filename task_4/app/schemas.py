from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: str
    priority: int = Field(ge=1, le=5)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['todo', 'in_progress', 'done']
        if v not in allowed:
            raise ValueError(f'status must be one of {allowed}')
        return v
    
class TaskResponse(TaskCreate):
    id: int
    owner_id: int
    
class StatusUpdate(BaseModel):
    status: str
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['todo', 'in_progress', 'done']
        if v not in allowed:
            raise ValueError(f'status must be one of {allowed}')
        return v
    
class User(BaseModel):
    id: int
    role: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        allowed = ['user', 'admin']
        if v not in allowed:
            raise ValueError(f'role must be one of {allowed}')
        return v

class StatsResponse(BaseModel):
    total_tasks: int
    by_status: Dict[str, int]