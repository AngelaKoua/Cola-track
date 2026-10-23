"""
Service layer for Notification system.

Handles:
- Creating and storing notifications
- Triggering business-event notifications (assignation, critical, deadline)
- Pushing real-time updates via WebSocket
- Read status management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timezone
import asyncio
import threading

from app.models.notification import Notification
from app.models.user import User
from app.models.incident import Incident
from app.services.ws_manager import ws_manager
from app.services.email_service import send_incident_assignment_email


# ============================================================================
# CRUD OPERATIONS
# ============================================================================

def create_notification(
    db: Session,
    user_id: int,
    incident_id: UUID,
    notif_type: str,
    titre: str,
    message: str,
    priority: str = "MEDIUM"
) -> Notification:
    """Create a notification and attempt WebSocket push."""
    notif = Notification(
        user_id=user_id,
        incident_id=incident_id,
        type=notif_type,
        titre=titre,
        message=message,
        priority=priority,
        is_read=False
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # Attempt async WebSocket push
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_push_notification(notif))
    except RuntimeError:
        # No running event loop (e.g., in sync threadpool context)
        # Use the global loop stored in ws_manager to safely dispatch the push
        if hasattr(ws_manager, 'loop') and ws_manager.loop and ws_manager.loop.is_running():
            asyncio.run_coroutine_threadsafe(_push_notification(notif), ws_manager.loop)


    return notif


async def _push_notification(notif: Notification):
    """Push notification payload via WebSocket."""
    payload = {
        "type": "notification",
        "notification_id": notif.id,
        "incident_id": str(notif.incident_id),
        "title": notif.titre,
        "message": notif.message,
        "priority": notif.priority,
        "notif_type": notif.type,
        "created_at": notif.created_at.isoformat() if notif.created_at else None
    }
    await ws_manager.send_to_user(notif.user_id, payload)


def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Notification]:
    """Get notifications for a user, ordered by newest first."""
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_notification_count(db: Session, user_id: int) -> int:
    """Get total notification count for a user."""
    return db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id
    ).scalar() or 0


def get_unread_count(db: Session, user_id: int) -> int:
    """Get unread notification count for badge display."""
    return db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).scalar() or 0


def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Mark a single notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    if notif:
        notif.is_read = True
        db.commit()
        db.refresh(notif)
    return notif


def mark_all_read(db: Session, user_id: int) -> int:
    """Mark all notifications as read for a user. Returns count updated."""
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({Notification.is_read: True})
    db.commit()
    return count


# ============================================================================
# BUSINESS EVENT TRIGGERS
# ============================================================================

def _get_user_id_by_username(db: Session, username: str) -> Optional[int]:
    """Lookup user ID from username."""
    user = db.query(User).filter(User.username == username).first()
    return user.id if user else None


def _get_manager_ids(db: Session) -> List[int]:
    """Get all active manager user IDs."""
    managers = db.query(User.id).filter(
        User.role == "manager",
        User.is_active == True
    ).all()
    return [m.id for m in managers]


def trigger_assignation_notification(db: Session, incident: Incident):
    """
    Trigger: Incident created or reassigned.
    Recipient: The assigned responsable.
    """
    user = db.query(User).filter(User.username == incident.responsable).first()
    if not user:
        return

    # Map criticite to priority
    priority_map = {
        "Critique": "URGENT",
        "Élevé": "HIGH",
        "Moyen": "MEDIUM",
        "Faible": "LOW"
    }
    priority = priority_map.get(incident.criticite, "MEDIUM")

    create_notification(
        db=db,
        user_id=user.id,
        incident_id=incident.id,
        notif_type="ASSIGNATION",
        titre="Nouvelle tache assignee",
        message=f"Incident sur {incident.equipement} ({incident.ligne}) - Criticite : {incident.criticite}",
        priority=priority
    )

    # Send an email if the user has an email address
    if user.email:
        # Send email in background to avoid blocking the HTTP response
        threading.Thread(
            target=send_incident_assignment_email,
            args=(user.email, user.username, incident)
        ).start()


def trigger_critical_notification(db: Session, incident: Incident):
    """
    Trigger: Incident with criticite == 'Critique' created.
    Recipients: Responsable + all Managers.
    """
    recipients: List[int] = []

    # Add responsable
    user_id = _get_user_id_by_username(db, incident.responsable)
    if user_id:
        recipients.append(user_id)

    # Add all managers
    manager_ids = _get_manager_ids(db)
    for mid in manager_ids:
        if mid not in recipients:
            recipients.append(mid)

    for uid in recipients:
        create_notification(
            db=db,
            user_id=uid,
            incident_id=incident.id,
            notif_type="CRITICAL",
            titre="Incident critique declare",
            message=f"Action immediate requise - {incident.ligne}, {incident.equipement}",
            priority="URGENT"
        )


def trigger_deadline_notifications(db: Session):
    """
    Trigger: Periodic check for overdue incidents.
    Recipients: Responsable + Managers.
    Called by the scheduler.
    """
    now = datetime.now(timezone.utc).date()

    # Find overdue incidents (deadline passed, not resolved)
    overdue = db.query(Incident).filter(
        Incident.deadline < now,
        Incident.statut != "Résolu"
    ).all()

    for incident in overdue:
        # Check if we already sent a DEADLINE notification for this incident today
        existing = db.query(Notification).filter(
            Notification.incident_id == incident.id,
            Notification.type == "DEADLINE",
            func.date(Notification.created_at) == now
        ).first()

        if existing:
            continue  # Already notified today

        recipients: List[int] = []

        user_id = _get_user_id_by_username(db, incident.responsable)
        if user_id:
            recipients.append(user_id)

        manager_ids = _get_manager_ids(db)
        for mid in manager_ids:
            if mid not in recipients:
                recipients.append(mid)

        for uid in recipients:
            create_notification(
                db=db,
                user_id=uid,
                incident_id=incident.id,
                notif_type="DEADLINE",
                titre="Deadline depassee",
                message=f"Incident sur {incident.equipement} ({incident.ligne}) non resolu dans les delais",
                priority="HIGH"
            )
