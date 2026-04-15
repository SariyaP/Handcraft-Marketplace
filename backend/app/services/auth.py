from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Role, User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.security import hash_password, verify_password


SYSTEM_ROLE_NAMES = ("customer", "maker", "admin")
REGISTERABLE_ROLE_NAMES = {"customer", "maker"}


class AuthenticationError(Exception):
    """Raised when login credentials or tokens are invalid."""


class DuplicateEmailError(Exception):
    """Raised when an email is already registered."""


class RoleAssignmentError(Exception):
    """Raised when an invalid role is used for registration."""


def ensure_system_roles(db: Session) -> None:
    existing_roles = set(db.scalars(select(Role.name)).all())

    created_role = False
    for role_name in SYSTEM_ROLE_NAMES:
        if role_name not in existing_roles:
            db.add(Role(name=role_name))
            created_role = True

    if created_role:
        db.commit()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(func.lower(User.email) == _normalize_email(email))
    )
    return db.scalar(statement)


def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(User.id == user_id)
    )
    return db.scalar(statement)


def create_user(db: Session, payload: RegisterRequest) -> User:
    ensure_system_roles(db)

    if payload.role not in REGISTERABLE_ROLE_NAMES:
        raise RoleAssignmentError("Users can only register as customer or maker.")

    existing_user = get_user_by_email(db, payload.email)
    if existing_user is not None:
        raise DuplicateEmailError("A user with this email already exists.")

    role = db.scalar(select(Role).where(Role.name == payload.role))
    if role is None:
        raise RoleAssignmentError("The selected role is not available.")

    user = User(
        email=_normalize_email(payload.email),
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()

    created_user = get_user_by_email(db, user.email)
    if created_user is None:
        raise AuthenticationError("Failed to load the created user.")

    return created_user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AuthenticationError("Invalid email or password.")

    if not user.is_active:
        raise AuthenticationError("This user account is inactive.")

    return user
