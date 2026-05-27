tasks_db = {}
current_id = 1

def get_all_tasks():
    return tasks_db

def add_task(task_data):
    global current_id
    task_data["id"] = current_id
    tasks_db[current_id] = task_data
    current_id += 1
    return task_data

def get_task(task_id):
    return tasks_db.get(task_id)

def update_task(task_id, task_data):
    if task_id in tasks_db:
        tasks_db[task_id].update(task_data)
        return tasks_db[task_id]
    return None

def delete_task(task_id):
    if task_id in tasks_db:
        del tasks_db[task_id]
        return True
    return False

def clear_all():
    global tasks_db, current_id
    tasks_db = {}
    current_id = 1