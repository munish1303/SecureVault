import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database.db"))


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash BLOB NOT NULL,
                    encryption_salt BLOB NOT NULL,
                    failed_attempts INTEGER NOT NULL DEFAULT 0,
                    lockout_until TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    site TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password BLOB NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
                )
                """
            )

    def create_user(self, username: str, password_hash: bytes, encryption_salt: bytes) -> bool:
        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO users (username, password_hash, encryption_salt, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, password_hash, encryption_salt, _utcnow().isoformat()),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_username(self, username: str) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    def reset_failed_attempts(self, user_id: int) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE users SET failed_attempts = 0, lockout_until = NULL WHERE id = ?",
                (user_id,),
            )

    def record_failed_login(self, user_id: int, max_attempts: int, lockout_minutes: int) -> Dict[str, Any]:
        with self.connect() as conn:
            user = conn.execute("SELECT failed_attempts FROM users WHERE id = ?", (user_id,)).fetchone()
            attempts = int(user["failed_attempts"]) + 1
            lockout_until = None

            if attempts >= max_attempts:
                lockout_until = (_utcnow() + timedelta(minutes=lockout_minutes)).isoformat()
                attempts = 0

            conn.execute(
                "UPDATE users SET failed_attempts = ?, lockout_until = ? WHERE id = ?",
                (attempts, lockout_until, user_id),
            )

        return {"attempts": attempts, "lockout_until": lockout_until}

    def add_password(self, user_id: int, site: str, username: str, encrypted_password: bytes, notes: str) -> None:
        now = _utcnow().isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO passwords (user_id, site, username, encrypted_password, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, site, username, encrypted_password, notes, now, now),
            )

    def get_passwords_for_user(self, user_id: int) -> List[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT id, site, username, notes, created_at, updated_at
                FROM passwords
                WHERE user_id = ?
                ORDER BY LOWER(site), LOWER(username)
                """,
                (user_id,),
            ).fetchall()

    def get_password_entry(self, entry_id: int, user_id: int) -> Optional[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM passwords WHERE id = ? AND user_id = ?",
                (entry_id, user_id),
            ).fetchone()

    def update_password(self, entry_id: int, user_id: int, site: str, username: str, encrypted_password: bytes, notes: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE passwords
                SET site = ?, username = ?, encrypted_password = ?, notes = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (site, username, encrypted_password, notes, _utcnow().isoformat(), entry_id, user_id),
            )

    def delete_password(self, entry_id: int, user_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM passwords WHERE id = ? AND user_id = ?", (entry_id, user_id))

    def log_event(self, user_id: Optional[int], action: str, details: str = "") -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO logs (user_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, action, details, _utcnow().isoformat()),
            )

    def recent_logs(self, user_id: int, limit: int = 25) -> List[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT id, action, details, timestamp
                FROM logs
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

    def recent_failed_login_count(self, user_id: int, minutes: int = 15) -> int:
        threshold = (_utcnow() - timedelta(minutes=minutes)).isoformat()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS total
                FROM logs
                WHERE user_id = ? AND action = 'LOGIN_FAILED' AND timestamp >= ?
                """,
                (user_id, threshold),
            ).fetchone()
        return int(row["total"]) if row else 0

    def suspicious_events(self, user_id: int) -> List[Dict[str, str]]:
        user = self.get_user_by_id(user_id)
        alerts: List[Dict[str, str]] = []

        if not user:
            return alerts

        failed_recently = self.recent_failed_login_count(user_id)
        if failed_recently >= 3:
            alerts.append(
                {
                    "level": "high",
                    "message": f"{failed_recently} failed login attempts were recorded in the last 15 minutes.",
                }
            )

        if user["lockout_until"]:
            lockout_until = datetime.fromisoformat(user["lockout_until"])
            if lockout_until > _utcnow():
                alerts.append(
                    {
                        "level": "medium",
                        "message": f"Account temporarily locked until {lockout_until.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}.",
                    }
                )

        recent_logs = self.recent_logs(user_id, limit=10)
        sensitive_views = sum(1 for log in recent_logs if log["action"] == "PASSWORD_VIEWED")
        if sensitive_views >= 5:
            alerts.append(
                {
                    "level": "medium",
                    "message": "Multiple password reveal actions occurred recently. Verify this activity was expected.",
                }
            )

        return alerts
