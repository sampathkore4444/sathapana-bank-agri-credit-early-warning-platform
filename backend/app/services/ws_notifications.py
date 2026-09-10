"""WebSocket-based in-app notification service.

Provides real-time push notifications for:
- New critical alerts
- Risk score changes
- Daily digest summaries
"""
import json
import asyncio
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.user_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.user_connections:
            self.user_connections[user_id] = [
                ws for ws in self.user_connections[user_id] if ws != websocket
            ]

    async def send_to_user(self, user_id: int, message: dict):
        if user_id in self.user_connections:
            for ws in self.user_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    async def broadcast(self, message: dict):
        for user_id, connections in self.user_connections.items():
            for ws in connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass

    def get_connected_users(self) -> list[int]:
        return [uid for uid, conns in self.user_connections.items() if conns]


manager = ConnectionManager()


async def notify_alert_created(alert_data: dict, assigned_rm_id: Optional[int] = None):
    """Push notification when a new alert is created."""
    message = {
        "type": "alert_created",
        "timestamp": datetime.utcnow().isoformat(),
        "data": alert_data,
    }

    if assigned_rm_id:
        await manager.send_to_user(assigned_rm_id, message)
    else:
        await manager.broadcast(message)


async def notify_risk_changed(farmer_id: int, old_bucket: str, new_bucket: str):
    """Push notification when risk bucket changes."""
    message = {
        "type": "risk_changed",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "farmer_id": farmer_id,
            "old_bucket": old_bucket,
            "new_bucket": new_bucket,
        },
    }
    await manager.broadcast(message)


async def notify_daily_digest(user_id: int, summary: dict):
    """Push daily digest summary."""
    message = {
        "type": "daily_digest",
        "timestamp": datetime.utcnow().isoformat(),
        "data": summary,
    }
    await manager.send_to_user(user_id, message)
