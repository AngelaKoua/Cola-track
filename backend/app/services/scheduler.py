"""
Background scheduler for periodic notification checks.

Runs a periodic deadline check (DEADLINE_CHECK_INTERVAL_SECONDS) to find
overdue incidents and generate DEADLINE notifications.
"""

import asyncio
import threading
from datetime import datetime

from app.database import SessionLocal
from app.services.notification_service import trigger_deadline_notifications


def check_deadlines():
    """Check for overdue incidents and create notifications."""
    db = SessionLocal()
    try:
        trigger_deadline_notifications(db)
    except Exception as e:
        print(f"[Scheduler] Error checking deadlines: {e}")
    finally:
        db.close()


async def deadline_scheduler(interval_seconds: int = 300):
    """
    Async scheduler that runs deadline checks periodically.
    Default: every 5 minutes (300 seconds).
    """
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            # Run the DB operation in a thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, check_deadlines)
            print(f"[Scheduler] Deadline check completed at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"[Scheduler] Error: {e}")
