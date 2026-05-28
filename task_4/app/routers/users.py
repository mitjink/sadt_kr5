from fastapi import Depends, APIRouter, HTTPException
from app.schemas import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only access your own user data")
    
    if user_id == current_user.id:
        return current_user
    
    return User(id=user_id, role="user")