from datetime import datetime, timezone
from typing import Optional, Tuple

import bcrypt

from .encryption import EncryptionManager
from .models import DatabaseManager


class AuthService:
    def __init__(self, db: DatabaseManager, max_attempts: int = 5, lockout_minutes: int = 10) -> None:
        self.db = db
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes

    def register_user(self, username: str, master_password: str) -> Tuple[bool, str]:
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters."
        if len(master_password) < 12:
            return False, "Master password must be at least 12 characters."

        password_hash = bcrypt.hashpw(master_password.encode("utf-8"), bcrypt.gensalt())
        encryption_salt = EncryptionManager.generate_salt()
        created = self.db.create_user(username.strip(), password_hash, encryption_salt)

        if not created:
            return False, "That username is already registered."

        user = self.db.get_user_by_username(username.strip())
        self.db.log_event(user["id"] if user else None, "REGISTER_SUCCESS", "New account created.")
        return True, "Registration successful. Please log in."

    def verify_login(self, username: str, master_password: str) -> Tuple[bool, str, Optional[dict]]:
        user = self.db.get_user_by_username(username.strip())
        if not user:
            self.db.log_event(None, "LOGIN_FAILED", f"Unknown username: {username.strip()}")
            return False, "Invalid username or password.", None

        if user["lockout_until"]:
            lockout_until = datetime.fromisoformat(user["lockout_until"])
            if lockout_until > datetime.now(timezone.utc):
                self.db.log_event(user["id"], "LOGIN_BLOCKED", "Login blocked during lockout window.")
                return False, f"Account locked until {lockout_until.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}.", None

        if bcrypt.checkpw(master_password.encode("utf-8"), user["password_hash"]):
            self.db.reset_failed_attempts(user["id"])
            self.db.log_event(user["id"], "LOGIN_SUCCESS", "User authenticated successfully.")
            return True, "Login successful.", dict(user)

        result = self.db.record_failed_login(user["id"], self.max_attempts, self.lockout_minutes)
        if result["lockout_until"]:
            self.db.log_event(user["id"], "SECURITY_ALERT", f"Account locked after too many failed logins until {result['lockout_until']}.")
            self.db.log_event(user["id"], "LOGIN_FAILED", "Invalid password and account locked.")
            return False, "Too many failed attempts. Account locked for 10 minutes.", None

        remaining = self.max_attempts - result["attempts"]
        self.db.log_event(user["id"], "LOGIN_FAILED", f"Invalid password. {remaining} attempts remaining before lockout.")
        return False, f"Invalid username or password. {remaining} attempts remaining.", None

    def verify_master_password(self, user_id: int, master_password: str) -> bool:
        user = self.db.get_user_by_id(user_id)
        return bool(user) and bcrypt.checkpw(master_password.encode("utf-8"), user["password_hash"])
