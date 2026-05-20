"""Unified `users` collection (role-based)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from werkzeug.security import generate_password_hash

from app.auth.helpers import ROLE_PRACTICE_USER, ROLE_RECRUITER


def insert_practice_user(db, name: str, email: str, password: str) -> Any:
    """Insert into unified users collection."""
    pw_hash = generate_password_hash(password)
    now = datetime.utcnow()
    doc = {
        "role": ROLE_PRACTICE_USER,
        "name": name,
        "email": email,
        "password_hash": pw_hash,
        "created_at": now,
    }
    res = db.users.insert_one(doc)
    return res.inserted_id


def insert_recruiter_user(
    db,
    email: str,
    password: str,
    company_name: str,
) -> Any:
    """Insert into unified users collection."""
    pw_hash = generate_password_hash(password)
    now = datetime.utcnow()
    doc = {
        "role": ROLE_RECRUITER,
        "name": company_name,
        "email": email,
        "company_name": company_name,
        "password_hash": pw_hash,
        "created_at": now,
    }
    res = db.users.insert_one(doc)
    return res.inserted_id


def find_practice_user_by_email(db, email: str) -> Optional[dict]:
    """Find practice user in unified collection."""
    return db.users.find_one({"email": email, "role": ROLE_PRACTICE_USER})


def find_recruiter_by_email(db, email: str) -> Optional[dict]:
    """Find recruiter in unified collection."""
    return db.users.find_one({"email": email, "role": ROLE_RECRUITER})
