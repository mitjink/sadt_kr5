from fastapi import FastAPI, HTTPException, Header
from typing import Optional, List
from app.schemas import taskCreate, taskResponse, statusUpdate
from app.storage import (
    add_task, get_all_tasks, get_task, update_task, delete_task, current_id as storage_current_id
)

app = FastAPI()

@app.post("/tasks", response_model=taskResponse, status_code=201)
def create_task(
    task: taskCreate,
    x_user_id: Optional[str] = Header(None)
):
    if x_user_id is None: 
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        owner_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
    
    task_data = task.model_dump()
    task_data["owner_id"] = owner_id
    
    created_task = add_task(task_data)
    return created_task

@app.get("/tasks", response_model=List[taskResponse])
def list_tasks(
    x_user_id: Optional[str] = Header(None),
    status: Optional[str] = None,
    min_priority: Optional[int] = None
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        owner_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
    
    all_tasks = get_all_tasks()
    
    user_tasks = [task for task in all_tasks.values() if task["owner_id"] == owner_id]
    
    if status:
        user_tasks = [t for t in user_tasks if t["status"] == status]
        
    if min_priority is not None:
        user_tasks = [t for t in user_tasks if t["priority"] >= min_priority]
            
    return user_tasks

@app.get("/tasks/{task_id}", response_model=taskResponse)
def get_task_by_id(
    task_id: int,
    x_user_id: Optional[str] = Header(None)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try: 
        owner_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
    
    task = get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["owner_id"] != owner_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@app.patch("/tasks/{task_id}/status", response_model=taskResponse)
def update_task_status(
    task_id: int,
    status_update: statusUpdate,
    x_user_id: Optional[str] = Header(None)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        owner_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
    
    task = get_task(task_id)
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["owner_id"] != owner_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = update_task(task_id, {"status": status_update.status})
    
    return updated_task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_taqsk_by_id(
    task_id: int,
    x_user_id: Optional[str] = Header(None)
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    
    try:
        owner_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id format")
    
    task = get_task(task_id)
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["owner_id"] != owner_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    delete_task(task_id)
    return