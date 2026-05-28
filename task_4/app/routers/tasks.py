from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from app.schemas import TaskCreate, TaskResponse, StatusUpdate, User
from app.dependencies import get_current_user
from app import storage

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    task_data = task.model_dump()
    task_data["owner_id"] = current_user.id
    created_task = storage.add_task(task_data)
    return created_task

@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
    min_priority: Optional[int] = None
):
    all_tasks = storage.get_all_tasks()
    
    user_tasks = [task for task in all_tasks.values() if task["owner_id"] == current_user.id]
    
    if status:
        user_tasks = [t for t in user_tasks if t["status"] == status]
    if min_priority is not None:
        user_tasks = [t for t in user_tasks if t["priority"] >= min_priority]
    return user_tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    task = storage.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["owner_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int, 
    status_update: StatusUpdate,
    current_user: User = Depends(get_current_user)
):
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["owner_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated = storage.update_task(task_id, {"status": status_update.status})
    return updated

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user)
):
    task = storage.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["owner_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    storage.delete_task(task_id)
    return