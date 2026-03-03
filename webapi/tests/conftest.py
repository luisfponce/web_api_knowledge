import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool


sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import myapp
from db.db_connection import get_session
from db.redis_connection import get_redis
from auth.auth_service import crear_jwt
from models.user import User
from models.prompts import Prompts


class FakeRedis:
    def __init__(self):
        self.store: dict[str, str] = {}

    def exists(self, key: str) -> bool:
        return key in self.store

    def setex(self, key: str, ttl: int, value: str):
        self.store[key] = value

    def get(self, key: str):
        return self.store.get(key)


@pytest.fixture
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    return test_engine


@pytest.fixture
def db_session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def client(db_session, fake_redis):
    def _override_get_session():
        yield db_session

    def _override_get_redis():
        yield fake_redis

    myapp.dependency_overrides[get_session] = _override_get_session
    myapp.dependency_overrides[get_redis] = _override_get_redis

    with TestClient(myapp, raise_server_exceptions=False) as test_client:
        yield test_client

    myapp.dependency_overrides.clear()


@pytest.fixture
def user_payload():
    return {
        "username": "pytest_user",
        "name": "Py",
        "last_name": "Tester",
        "phone": 5512345678,
        "email": "pytest_user@example.com",
        "hashed_password": "pytest_password",
    }


@pytest.fixture
def created_user(db_session):
    user = User(
        username="base_user",
        name="Base",
        last_name="User",
        phone=5500000001,
        email="base_user@example.com",
        hashed_password="base_password",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_header(created_user):
    token = crear_jwt({"sub": created_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def created_prompt(db_session, created_user):
    prompt = Prompts(
        user_id=created_user.id,
        model_name="gpt-4.1",
        prompt_text="existing prompt",
        category="qa",
        rate="high",
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)
    return prompt
