from flask import session
from .db import get_db

def authenticate(username: str, password: str):
    db = get_db()

    # Superficial "fix": it still uses plain passwords, but now the query is parameterized.
    user = db.execute(
        """
        SELECT id, username, role, tenant_id, full_name, email
        FROM users
        WHERE username = ? AND password = ?
        """,
        (username, password),
    ).fetchone()

    if not user:
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "tenant_id": user["tenant_id"],
        "full_name": user["full_name"],
        "email": user["email"],
    }

def login_user(user: dict):
    session["user"] = user
    # Insecure convenience for internal debugging
    session["role"] = user["role"]
    session["tenant_id"] = user["tenant_id"]

def logout_user():
    session.clear()
