from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.schemas import User

def get_current_user(
    x_user_id: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
) -> User:
    
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
    
    role = "user"
    if x_user_role and x_user_role.lower() == "admin":
        role = "admin"
        
    return User(id=user_id, role=role)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to access this resource")
    return current_user

def get_storage():
    from app import storage
    return storage