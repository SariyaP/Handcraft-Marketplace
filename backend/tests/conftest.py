from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Role, User, load_all_models
from app.schemas.auth import RegisterRequest
from app.services.auth import create_user, ensure_system_roles
from app.utils.security import hash_password


load_all_models()

TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    ensure_system_roles(db)
    db.close()
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_role(db, name: str) -> Role:
    return db.scalar(select(Role).where(Role.name == name))


@pytest.fixture
def customer_user(db_session):
    return create_user(
        db_session,
        RegisterRequest(
            email="customer@example.com",
            full_name="Customer One",
            password="password123",
            role="customer",
        ),
    )


@pytest.fixture
def second_customer_user(db_session):
    return create_user(
        db_session,
        RegisterRequest(
            email="customer.two@example.com",
            full_name="Customer Two",
            password="password123",
            role="customer",
        ),
    )


@pytest.fixture
def maker_user(db_session):
    return create_user(
        db_session,
        RegisterRequest(
            email="maker@example.com",
            full_name="Maker One",
            password="password123",
            role="maker",
        ),
    )


@pytest.fixture
def second_maker_user(db_session):
    return create_user(
        db_session,
        RegisterRequest(
            email="maker.two@example.com",
            full_name="Maker Two",
            password="password123",
            role="maker",
        ),
    )


@pytest.fixture
def admin_user(db_session):
    admin_role = _get_role(db_session, "admin")
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        password_hash=hash_password("password123"),
        role=admin_role,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


def auth_headers_for(client: TestClient, email: str, password: str = "password123") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
