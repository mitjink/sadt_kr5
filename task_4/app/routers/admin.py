from fastapi import APIRouter, Depends, HTTPException
from app.schemas import StatsResponse, User
from app.dependencies import require_admin
import app.storage as storage

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats", response_model=StatsResponse)
def get_stats(
    admin_user: User = Depends(require_admin)
):
    return storage.get_stats()

@router.delete("/tasks/{task_id}", status_code=204)
def delete_any_task(
    task_id: int,
    admin_user: User = Depends(require_admin)
):
    deleted = storage.delete_any_task(task_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return