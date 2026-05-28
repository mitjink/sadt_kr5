from app.storage import clear_all


def test_users_me_returns_current_user(client):
    response = client.get(
        "/users/me",
        headers={
            "X-User-Id": "42",
            "X-User-Role": "admin"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == 42
    assert data["role"] == "admin"


def test_users_me_default_role(client):
    response = client.get(
        "/users/me",
        headers={"X-User-Id": "10"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == 10
    assert data["role"] == "user" 


def test_no_auth_header_returns_401(client):
    response = client.get("/users/me")
    
    assert response.status_code == 401
    assert "X-User-Id header required" in response.json()["detail"]


def test_invalid_user_id_returns_401(client):
    response = client.get(
        "/users/me",
        headers={"X-User-Id": "not_a_number"}
    )
    
    assert response.status_code == 401
    assert "Invalid X-User-Id format" in response.json()["detail"]


def test_regular_user_cannot_access_admin_stats(client):
    response = client.get(
        "/admin/stats",
        headers={"X-User-Id": "10"} 
    )
    
    assert response.status_code == 403
    assert "don't have permission" in response.json()["detail"].lower()


def test_admin_can_access_stats(client):
    client.post(
        "/tasks",
        json={"title": "Задача 10", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"}
    )
    
    client.post(
        "/tasks",
        json={"title": "Задача 20", "status": "done", "priority": 2},
        headers={"X-User-Id": "20"}
    )
    
    client.post(
        "/tasks",
        json={"title": "Задача 30", "status": "in_progress", "priority": 3},
        headers={"X-User-Id": "30"}
    )
    
    response = client.get(
        "/admin/stats",
        headers={
            "X-User-Id": "1",
            "X-User-Role": "admin"
        }
    )
    
    assert response.status_code == 200
    stats = response.json()
    
    assert stats["total_tasks"] == 3
    assert stats["by_status"]["todo"] == 1
    assert stats["by_status"]["in_progress"] == 1
    assert stats["by_status"]["done"] == 1


def test_regular_user_cannot_delete_others_task(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Чужая задача", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "20"} 
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    
    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    assert get_response.status_code == 200


def test_admin_can_delete_any_task_via_admin_endpoint(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Задача админа", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"}
    )
    task_id = create_response.json()["id"]
    
    response = client.delete(
        f"/admin/tasks/{task_id}",
        headers={
            "X-User-Id": "1",
            "X-User-Role": "admin"
        }
    )
    
    assert response.status_code == 204 
    
    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-Id": "10"}
    )
    assert get_response.status_code == 404


def test_admin_cannot_delete_nonexistent_task(client):
    response = client.delete(
        "/admin/tasks/99999", 
        headers={
            "X-User-Id": "1",
            "X-User-Role": "admin"
        }
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_swagger_tags_present(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi = response.json()
    paths = openapi.get("paths", {})
    
    has_tasks_tag = False
    has_users_tag = False
    has_admin_tag = False
    
    for path, methods in paths.items():
        for method, details in methods.items():
            tags = details.get("tags", [])
            if "tasks" in tags:
                has_tasks_tag = True
            if "users" in tags:
                has_users_tag = True
            if "admin" in tags:
                has_admin_tag = True
    
    assert has_tasks_tag, "Missing 'tasks' tag in OpenAPI"
    assert has_users_tag, "Missing 'users' tag in OpenAPI"
    assert has_admin_tag, "Missing 'admin' tag in OpenAPI"