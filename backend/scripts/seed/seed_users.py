from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.routers.auth import get_password_hash

def seed_users():
    db = SessionLocal()
    try:
        users = [
            {"username": "technician", "password": "tech123", "role": "technician"},
            {"username": "manager", "password": "manager123", "role": "manager"},

        ]

        for user_data in users:
            user = db.query(User).filter(User.username == user_data["username"]).first()
            if not user:
                hashed_password = get_password_hash(user_data["password"])
                new_user = User(
                    username=user_data["username"],
                    password_hash=hashed_password,
                    role=user_data['role']
                )
                db.add(new_user)
                print(f"Created user: {user_data['username']}")
            else:
                print(f"User already exists: {user_data['username']}")
        
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
