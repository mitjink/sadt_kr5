from fastapi.testclient import TestClient
from app.main import app
import pytest

def test_websocket_connect_success(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "system"
        assert data["username"] == "alice"
        assert "присоединился" in data["text"]
        
def test_websocket_missing_username(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/python"):
            pass

def test_websocket_empty_username(client):
    username = "        "
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/rooms/python?username={username}"):
            pass
        
def test_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        welcome = websocket.receive_json()
        assert welcome["type"] == "system"
        
        message_to_send = {
            "type": "message",
            "text": "Тест отправки и получения сообщений"
        }
        websocket.send_json(message_to_send)
        
        received = websocket.receive_json()
        
        assert received["type"] == "message"
        assert received["room_id"] == "python"
        assert received["username"] == "alice"
        assert received["text"] == "Тест отправки и получения сообщений"
        
def test_two_clients_in_one_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        
        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            bob.receive_json() 
            
            alice.send_json({
                "type": "message",
                "text": "Hi, Bob!"
            })
            
            received_by_bob = bob.receive_json()
            assert received_by_bob["username"] == "alice"
            assert received_by_bob["text"] == "Hi, Bob!"
            
            received_by_alice = alice.receive_json()
            assert "text" in received_by_alice
            
def test_different_rooms_isolation(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        with client.websocket_connect("ws/rooms/javascript?username=bob") as bob:
            bob.receive_json()
            
            alice.send_json({
                "type": "message",
                "text": "Only for Pyhton room"
            })
            
            alice.receive_json()
            
            import asyncio
            
            def try_receive():
                with pytest.raises(Exception):
                    bob.receive_json(timeout=1)
                    
            try_receive()
            
def test_message_too_long(client):
    with client.websocket_connect("ws//rooms/python?username=alice") as websocket:
        websocket.receive_json()
        long_text = "*" * 301
        websocket.send_json({
            "type": "message",
            "text": long_text
        })
        
        error_response = websocket.receive_json()
        assert error_response["type"] == "error"
        assert "too long" in error_response["detail"].lower()
        
        with pytest.raises(Exception):
            websocket.receive_json(timeout=1)
            
def test_disconnect_removes_user(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json() 
        response = client.get("/rooms/python/users")
        assert response.status_code == 200
        assert response.json()["users"] == ["alice"]
    
    response = client.get("/rooms/python/users")
    assert response.status_code == 200
    assert response.json()["users"] == []