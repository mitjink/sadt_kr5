from typing import Dict, Optional

tasks_db: Dict[int, dict] = {}
current_id: int = 1


def get_all_tasks() -> Dict[int, dict]:
    return tasks_db


def add_task(task_data: dict) -> dict:
    global current_id
    task_data["id"] = current_id
    tasks_db[current_id] = task_data
    current_id += 1
    return task_data


def get_task(task_id: int) -> Optional[dict]:
    return tasks_db.get(task_id)


def update_task(task_id: int, task_data: dict) -> Optional[dict]:
    if task_id in tasks_db:
        tasks_db[task_id].update(task_data)
        return tasks_db[task_id]
    return None


def delete_task(task_id: int) -> bool:
    if task_id in tasks_db:
        del tasks_db[task_id]
        return True
    return False


def clear_all():
    global tasks_db, current_id
    tasks_db = {}
    current_id = 1

def get_stats() -> dict:
    total = len(tasks_db)
    
    by_status = {
        "todo": 0,
        "in_progress": 0,
        "done": 0
    }
    
    for task in tasks_db.values():
        status = task.get("status")
        if status in by_status:
            by_status[status] += 1
    
    return {
        "total_tasks": total,
        "by_status": by_status
    }


def delete_any_task(task_id: int) -> bool:
    if task_id in tasks_db:
        del tasks_db[task_id]
        return True
    return False