"""
API Router for Notification Management.

Endpoints for reading and managing user notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse
)
from app.services.notification_service import (
    get_user_notifications,
    get_user_notification_count,
    get_unread_count,
    mark_as_read,
    mark_all_read
)
from app.models.user import User

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    responses={404: {"description": "Not found"}}
)


def _get_user_id_from_query(user_id: int) -> int:
    """
    Temporary: Accept user_id as query param.
    In production, extract from JWT token.
    """
    return user_id


@router.get("/", response_model=NotificationListResponse)
def read_notifications(
    user_id: int = Query(..., description="ID of the user"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get notifications for a user."""
    notifications = get_user_notifications(db, user_id=user_id, skip=skip, limit=limit)
    total = get_user_notification_count(db, user_id=user_id)
    unread = get_unread_count(db, user_id=user_id)

    return {
        "total": total,
        "unread_count": unread,
        "data": notifications
    }


@router.get("/unread-count", response_model=UnreadCountResponse)
def read_unread_count(
    user_id: int = Query(..., description="ID of the user"),
    db: Session = Depends(get_db)
):
    """Get unread notification count for badge."""
    count = get_unread_count(db, user_id=user_id)
    return {"count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    user_id: int = Query(..., description="ID of the user"),
    db: Session = Depends(get_db)
):
    """Mark a single notification as read."""
    notif = mark_as_read(db, notification_id=notification_id, user_id=user_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.patch("/read-all")
def mark_all_notifications_read(
    user_id: int = Query(..., description="ID of the user"),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for a user."""
    count = mark_all_read(db, user_id=user_id)
    return {"message": f"{count} notifications marked as read"}
