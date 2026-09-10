"""WebSocket route for real-time in-app notifications."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.auth_service import decode_token
from app.services.ws_notifications import manager

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
):
    """WebSocket endpoint for real-time notifications.

    Connect with: ws://localhost:8000/api/ws/notifications?token=<jwt>
    """
    # Validate token
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive, listen for pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
