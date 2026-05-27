from app.storage import clear_all

def test_create_task_success(client):
    task_data = {
        "title": "Контрольная",
        "description": "Сдать контрольную",
        "status": "in_progress",
        "priority": 5
    }
    
    response = client.post(
        "/tasks",
        json = task_data,
        headers={"X-User-Id": "10"}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert data["priority"] == task_data["priority"]
    
    assert data["owner_id"] == 10
  
    list_response = client.get("/tasks", headers={"X-User-Id": "10"})
    tasks = list_response.json()
    
    assert len(tasks) == 1
    assert tasks[0]["id"] == data["id"]
    
def test_create_task_invalid_title(client):
    task_data = {
        "title": "AB",
        "description": "Тест с коротким названием задачи",
        "status": "todo",
        "priority": 2
    }
    
    response = client.post(
        "/tasks",
        json=task_data,
        headers={"X-User-Id": "10"}
    )
    
    assert response.status_code == 422
    
    error_data = response.json()
    
    assert "detail" in error_data
    errors = error_data["detail"]
    
    found_title_error = False
    for error in errors:
        if "title" in str(error.get("loc", [])):
            found_title_error = True
            break
    assert found_title_error, "Ожидалась ошибка валидации для поля title"
    
    
def test_create_task_no_auth(client):
    task_data = {
        "title": "Задача без авторизации",
        "description": "Задача без авторизации",
        "status": "done",
        "priority": 3
    }
    
    response = client.post(
        "/tasks",
        json=task_data
    )
    
    assert response.status_code == 401
    error_data = response.json()
    assert error_data["detail"] == "X-User-Id header required"
    
    list_response = client.get("/tasks", headers={"X-User-Id": "10"})
    tasks = list_response.json()
    
    assert tasks == []
    
def test_user_sees_only_own_tasks(client):
    response_user1 = client.post(
        "/tasks",
        json={
            "title": "Задача пользователя 10",
            "status": "todo",
            "priority": 2
        },
        headers={"X-User-Id": "10"}
    )
    
    assert response_user1.status_code == 201
    task_user1_id = response_user1.json()["id"]
    
    response_user2 = client.post(
        "/tasks",
        json={
            "title": "Задача пользователя 20",
            "status": "todo",
            "priority": 4
        },
        headers={"X-User-Id": "20"}
    )
    assert response_user2.status_code == 201
    task_user2_id = response_user2.json()["id"]
    
    response = client.get("/tasks", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    
    tasks = response.json()
    assert len(tasks) == 1
    
    assert tasks[0]["id"] == task_user1_id
    assert tasks[0]["title"] == "Задача пользователя 10"
    
    response = client.get(
        f"/tasks/{task_user2_id}",
        headers={"X-User-Id": "10"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    
def task_filter_tasks(client):
    tasks_list = [
        {"title": "Todo низкий", "status": "todo", "priority": 1},
        {"title": "Todo высокий", "status": "todo", "priority": 5},
        {"title": "In progress", "status": "in_progress", "priority": 3},
        {"title": "Done", "status": "done", "priority": 4},
    ]
    
    for task in tasks_list:
        response = client.post(
            "/tasks",
            json=task,
            headers={"X-User-Id": "10"}
        )
        assert response.status_code == 201
        
    response = client.get(
        "/tasks?status=todo",
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 200
    
    tasks = response.json()
    
    assert len(tasks) == 2
    for task in tasks:
        assert task["status"] == "todo"
    
    response = client.get(
        "/tasks?min_priority=4",
        headers={"X-User-Id": "10"}
    )
    tasks = response.json()
    assert len(tasks) == 2
    for task in tasks:
        assert task["priority"] >= 4
        
    response = client.get(
        "/tasks?status=todo&min_priority=3",
        headers={"X-User-Id": "10"}
    )
    
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Todo высокий"
    assert tasks[0]["status"] == "todo"
    assert tasks[0]["priority"] == 5
    
def test_update_status(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Задача для изменения статуса",
            "status": "todo",
            "priority": 2
        },
        headers={"X-User-Id": "10"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    assert get_response.json()["status"] == "todo"
    
    update_response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers={"X-User-Id": "10"}
    )
    
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["status"] == "done"
    
    get_again_response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    assert get_again_response.json()["status"] == "done"
    
    assert updated_task["title"] == "Задача для изменения статуса"
    assert updated_task["priority"] == 2
    
def test_access_other_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Test 7",
            "status": "todo",
            "priority": 5
        },
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    
    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "20"}
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    
    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers={"X-User-Id": "20"}
    )
    
    assert response.status_code == 404
    
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "20"}
    )
    
    assert response.status_code == 404
    
    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 200
    
def test_delete_task(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Задача для удаления",
            "status": "todo",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    assert get_response.status_code == 200
    
    delete_response = client.delete(
        f"tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    
    assert delete_response.status_code == 204
    assert delete_response.text == ""
    
    get_response_after_delete = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    
    assert get_response_after_delete.status_code == 404
    
    list_response = client.get(
        "/tasks",
        headers={"X-User-Id": "10"}
    )
    tasks = list_response.json()
    assert tasks == []