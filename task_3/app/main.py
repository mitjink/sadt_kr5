from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from typing import Optional
from app.room_manager import RoomManager

app = FastAPI()

manager = RoomManager()

@app.websocket("/ws/rooms/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    username: Optional[str] = Query(None)
):
    if not username or not username.strip():
        await websocket.close(code=1008, reason="username required")
        return
    username = username.strip()
    
    await manager.connect(room_id, username, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("text", "")
            
            if len(message_text) > 300:
                error_payload = {
                    "type": "error",
                    "detail": "Message is too long"
                }
                await manager.send_to_user(websocket, error_payload)
                continue
            
            broadcast_payload = {
                "type": "message",
                "room_id": room_id,
                "username": username,
                "text": message_text
            }
            await manager.broadcast(room_id, broadcast_payload)
            
    except WebSocketDisconnect:
        manager.disconnect(room_id, username, websocket)
        leave_message = {
            "type": "system",
            "room_id": room_id,
            "username": username,
            "text": f"{username} покинул чат"
        }
        await manager.broadcast(room_id, leave_message)
        
@app.get("/rooms/{room_id}/users")
def get_room_users(room_id: str):
    users_list = manager.get_users(room_id)
    return {"room_id": room_id, "users": users_list}