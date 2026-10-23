"""
WebSocket Connection Manager for real-time notifications.

Manages active WebSocket connections per user_id,
allowing targeted notification delivery.
"""

from fastapi import WebSocket
from typing import Dict
import json


class ConnectionManager:
    """
    Manages WebSocket connections mapped by user_id.
    """

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.loop = None  # Will be set in main.py lifespan


    async def connect(self, user_id: int, websocket: WebSocket):
        """Accept and register a WebSocket connection for a user."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Remove a user's WebSocket connection."""
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, data: dict):
        """Send a JSON payload to a specific user if connected."""
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data, default=str))
            except Exception:
                # Connection might be stale, remove it
                self.disconnect(user_id)

    async def broadcast(self, data: dict, user_ids: list[int]):
        """Send a payload to multiple users."""
        for user_id in user_ids:
            await self.send_to_user(user_id, data)


# Global singleton instance
ws_manager = ConnectionManager()
