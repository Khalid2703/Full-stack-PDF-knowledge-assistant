"""
List users in the application's database (development helper).

Run from the `backend` folder with your virtualenv active:

Windows PowerShell:
  .\.venv\Scripts\Activate
  python .\scripts\list_users.py

This script is for local development only.
"""
from app.database import SessionLocal
from app.models.user import User


def main():
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id).all()
        if not users:
            print("No users found.")
            return

        for u in users:
            print(
                f"id={u.id} email={u.email!r} name={u.name!r} is_active={u.is_active} "
                f"created_at={u.created_at} hashed_len={len(u.hashed_password or '')}"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
