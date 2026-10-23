from sqlalchemy import text
from app.database import engine

def check_users():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT username, role, is_active FROM users"))
        users = result.fetchall()
        print(f"Found {len(users)} users:")
        for u in users:
            print(f"- {u.username} ({u.role}) Active: {u.is_active}")

if __name__ == "__main__":
    check_users()
