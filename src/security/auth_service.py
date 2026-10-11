import time
import secrets
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from src.database.db import Database, get_db
from src.security.password import hash_password, verify_password
from src.services.logging_service import logger

SESSION_TTL_SECONDS = 86400 * 7  # 7 days

@dataclass
class User:
    id: str
    username: str
    full_name: str
    role: str  # 'guest', 'staff', 'admin'
    is_active: bool
    created_at: float
    updated_at: float

@dataclass
class SessionInfo:
    token: str
    user_id: str
    username: str
    full_name: str
    role: str
    expires_at: float
    assigned_store_ids: List[str]

class AuthService:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        row = self.db.fetchone("SELECT * FROM users WHERE id = ?", (user_id,))
        if not row:
            return None
        return User(
            id=row["id"],
            username=row["username"],
            full_name=row["full_name"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.db.fetchone("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))

    def get_staff_store_ids(self, user_id: str) -> List[str]:
        rows = self.db.fetchall("SELECT store_id FROM staff_store_assignments WHERE user_id = ?", (user_id,))
        return [r["store_id"] for r in rows]

    def login(self, username: str, password: str, ip_address: str = "", user_agent: str = "") -> Optional[SessionInfo]:
        user_row = self.get_user_by_username(username)
        if not user_row or not user_row["is_active"]:
            logger.warning(f"Failed login attempt for username: {username} (Invalid user or inactive)")
            return None

        if not verify_password(password, user_row["password_hash"]):
            logger.warning(f"Failed login attempt for username: {username} (Wrong password)")
            return None

        now = time.time()
        token = secrets.token_hex(32)
        expires_at = now + SESSION_TTL_SECONDS

        with self.db.transaction() as conn:
            conn.execute("""
                INSERT INTO sessions (token, user_id, expires_at, created_at, last_active, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (token, user_row["id"], expires_at, now, now, ip_address, user_agent))

        self.log_audit(
            user_id=user_row["id"],
            username=user_row["username"],
            role=user_row["role"],
            action="LOGIN",
            resource="AUTH",
            details="User logged in successfully",
            ip_address=ip_address
        )

        assigned_stores = self.get_staff_store_ids(user_row["id"]) if user_row["role"] == "staff" else []

        return SessionInfo(
            token=token,
            user_id=user_row["id"],
            username=user_row["username"],
            full_name=user_row["full_name"],
            role=user_row["role"],
            expires_at=expires_at,
            assigned_store_ids=assigned_stores
        )

    def logout(self, token: str) -> bool:
        session = self.get_session(token)
        if session:
            self.log_audit(
                user_id=session.user_id,
                username=session.username,
                role=session.role,
                action="LOGOUT",
                resource="AUTH",
                details="User logged out"
            )
        self.db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        return True

    def get_session(self, token: str) -> Optional[SessionInfo]:
        if not token:
            return None

        now = time.time()
        query = """
            SELECT s.token, s.user_id, s.expires_at, u.username, u.full_name, u.role, u.is_active
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ? AND u.is_active = 1
        """
        row = self.db.fetchone(query, (token, now))
        if not row:
            return None

        # Update last_active
        self.db.execute("UPDATE sessions SET last_active = ? WHERE token = ?", (now, token))

        assigned_stores = self.get_staff_store_ids(row["user_id"]) if row["role"] == "staff" else []

        return SessionInfo(
            token=row["token"],
            user_id=row["user_id"],
            username=row["username"],
            full_name=row["full_name"],
            role=row["role"],
            expires_at=row["expires_at"],
            assigned_store_ids=assigned_stores
        )

    def log_audit(self, user_id: Optional[str], username: Optional[str], role: Optional[str],
                  action: str, resource: str, details: str = "", ip_address: str = ""):
        try:
            audit_id = f"aud_{int(time.time()*1000)}_{secrets.token_hex(4)}"
            self.db.execute("""
                INSERT INTO audit_logs (id, user_id, username, role, action, resource, details, ip_address, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (audit_id, user_id, username, role, action, resource, details, ip_address, time.time()))
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")

    def create_user(self, username: str, password: str, full_name: str, role: str,
                    store_ids: Optional[List[str]] = None, creator_session: Optional[SessionInfo] = None) -> User:
        username = username.strip().lower()
        if self.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        if role not in ("staff", "admin"):
            raise ValueError(f"Invalid role '{role}' for user creation")

        user_id = f"usr_{secrets.token_hex(6)}"
        pwd_hash = hash_password(password)
        now = time.time()

        with self.db.transaction() as conn:
            conn.execute("""
                INSERT INTO users (id, username, password_hash, full_name, role, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, pwd_hash, full_name, role, 1, now, now))

            if role == "staff" and store_ids:
                for sid in store_ids:
                    asn_id = f"asn_{secrets.token_hex(6)}"
                    conn.execute("""
                        INSERT INTO staff_store_assignments (id, user_id, store_id, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (asn_id, user_id, sid, now))

        if creator_session:
            self.log_audit(
                user_id=creator_session.user_id,
                username=creator_session.username,
                role=creator_session.role,
                action="CREATE_USER",
                resource="USERS",
                details=f"Created user {username} with role {role}"
            )

        return User(id=user_id, username=username, full_name=full_name, role=role, is_active=True, created_at=now, updated_at=now)

    def set_user_active(self, user_id: str, is_active: bool, admin_session: SessionInfo) -> bool:
        self.db.execute("UPDATE users SET is_active = ?, updated_at = ? WHERE id = ?", (1 if is_active else 0, time.time(), user_id))
        self.log_audit(
            user_id=admin_session.user_id,
            username=admin_session.username,
            role=admin_session.role,
            action="TOGGLE_USER_ACTIVE",
            resource="USERS",
            details=f"Set user {user_id} active status to {is_active}"
        )
        return True
