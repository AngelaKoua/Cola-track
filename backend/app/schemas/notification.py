"""
Pydantic schemas for Notification system.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class NotificationResponse(BaseModel):
    """Schema for a single notification in API responses."""
    id: int
    user_id: int
    incident_id: UUID
    type: str  # ASSIGNATION, DEADLINE, CRITICAL
    titre: str
    message: str
    priority: str  # LOW, MEDIUM, HIGH, URGENT
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Schema for paginated list of notifications."""
    total: int
    unread_count: int
    data: list[NotificationResponse]


class UnreadCountResponse(BaseModel):
    """Schema for unread count badge."""
    count: int
