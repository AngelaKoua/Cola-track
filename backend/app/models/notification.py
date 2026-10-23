"""
SQLAlchemy ORM model for Internal Notifications.

Stores business-event notifications tied to incidents,
with user targeting, priority levels, and read status.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class Notification(Base):
    """
    Notification Model.

    Table: notifications
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Target user (FK to users table)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Related incident (FK to incidents table)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)

    # Notification type: ASSIGNATION, DEADLINE, CRITICAL
    type = Column(String(50), nullable=False)

    # Content
    titre = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Priority: LOW, MEDIUM, HIGH, URGENT
    priority = Column(String(20), nullable=False, default="MEDIUM")

    # Read status
    is_read = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Notification(id={self.id}, user={self.user_id}, type={self.type}, read={self.is_read})>"
