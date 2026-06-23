"""Authentication and authorization module."""

import bcrypt
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database import User, UserRole, AuditLog


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: UserRole = UserRole.VIEWER,
    department: str = None,
    approval_limit: float = 0.0
) -> User:
    """Create a new user."""
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        department=department,
        approval_limit=approval_limit
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = db.query(User).filter(User.username == username).first()
    if user and user.is_active and verify_password(password, user.password_hash):
        return user
    return None


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def log_audit(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str = None,
    entity_id: int = None,
    details: str = None
):
    """Log an audit entry."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(log)
    db.commit()


def can_approve_invoice(user: User, amount: float) -> bool:
    """Check if user can approve an invoice of given amount."""
    if user.role == UserRole.ADMIN:
        return True
    if user.role == UserRole.APPROVER and amount <= user.approval_limit:
        return True
    return False


def get_permission_level(role: UserRole) -> int:
    """Get numeric permission level for a role."""
    levels = {
        UserRole.VIEWER: 1,
        UserRole.CLERK: 2,
        UserRole.APPROVER: 3,
        UserRole.ADMIN: 4
    }
    return levels.get(role, 0)
