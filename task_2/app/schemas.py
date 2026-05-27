from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional

class taskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: str
    priority: int = Field(ge=1, le=5)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['todo', 'in_progress', 'done']
        if v not in allowed:
            raise ValueError(f'status mudt be one of {allowed}')
        return v
    
class taskResponse(taskCreate):
    id: int
    owner_id: int
    
class statusUpdate(BaseModel):
    status: str
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['todo', 'in_progress', 'done']
        if v not in allowed:
            raise ValueError(f'status must be in {allowed}')
        return v