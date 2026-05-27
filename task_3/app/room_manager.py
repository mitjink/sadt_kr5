from fastapi import WebSocket
from typing import Dict, Set


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self.usernames: Dict[WebSocket, str] = {}
    
    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(room_id, set()).add(websocket)
        self.usernames[websocket] = username
        
        join_message = {
            "type": "system",
            "room_id": room_id,
            "username": username,
            "text": f"{username} присоединился к чату"
        }
        await self.broadcast(room_id, join_message)
    
    def disconnect(self, room_id: str, username: str, websocket: WebSocket):
        room_connections = self.rooms.get(room_id)
        if room_connections:
            room_connections.discard(websocket)
            if not room_connections:
                self.rooms.pop(room_id, None)
        
        self.usernames.pop(websocket, None)
    
    async def broadcast(self, room_id: str, payload: dict):
        clients = self.rooms.get(room_id, set())
        for client in list(clients):
            try:
                await client.send_json(payload)
            except Exception:
                pass
    
    async def send_to_user(self, websocket: WebSocket, payload: dict):
        try:
            await websocket.send_json(payload)
        except Exception:
            pass
    
    def get_users(self, room_id: str):
        websockets_in_room = self.rooms.get(room_id, set())
        
        users_list = []
        for ws in websockets_in_room:
            username = self.usernames.get(ws)
            if username:
                users_list.append(username)
        
        return users_list