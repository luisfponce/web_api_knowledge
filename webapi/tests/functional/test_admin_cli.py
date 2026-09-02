import pytest
from sqlmodel import select

from auth.password_service import hash_password, verify_password
from admin_cli import (
    SuperAdminBootstrapError,
    _compose_host_fallback_db_url,
    bootstrap_super_admin,
)
from models.user import User


def test_bootstrap_super_admin_creates_first_god_user(db_session):
    result = bootstrap_super_admin(
        db_session,
        username="root_user",
        email="root@example.com",
        password="secret_password",
    )

    assert result.action == "created"
    assert result.user.role == "god"
    assert verify_password("secret_password", result.user.hashed_password)
    assert result.user.hashed_password.startswith("$argon2id$")

    stored = db_session.exec(select(User).where(User.username == "root_user")).one()
    assert stored.role == "god"


def test_bootstrap_super_admin_promotes_existing_user_when_no_god_exists(db_session):
    user = User(
        username="operator",
        name="Regular",
        last_name="User",
        email="operator@example.com",
        hashed_password=hash_password("old_password"),
    )
    db_session.add(user)
    db_session.commit()

    result = bootstrap_super_admin(
        db_session,
        username="operator",
        email="operator-admin@example.com",
        password="new_password",
        name="Ops",
        last_name="Admin",
    )

    assert result.action == "promoted"
    assert result.user.role == "god"
    assert result.user.email == "operator-admin@example.com"
    assert verify_password("new_password", result.user.hashed_password)
    assert result.user.hashed_password.startswith("$argon2id$")


def test_bootstrap_super_admin_is_idempotent_for_same_god_user(db_session):
    first = bootstrap_super_admin(
        db_session,
        username="root_user",
        email="root@example.com",
        password="secret_password",
    )
    original_hash = first.user.hashed_password

    second = bootstrap_super_admin(
        db_session,
        username="root_user",
        email="changed@example.com",
        password="different_password",
    )

    assert second.action == "already_exists"
    assert second.user.id == first.user.id
    assert second.user.email == "root@example.com"
    assert second.user.hashed_password == original_hash


def test_bootstrap_super_admin_refuses_when_another_god_exists(db_session):
    bootstrap_super_admin(
        db_session,
        username="root_user",
        email="root@example.com",
        password="secret_password",
    )

    with pytest.raises(SuperAdminBootstrapError, match="super admin already exists"):
        bootstrap_super_admin(
            db_session,
            username="second_root",
            email="second@example.com",
            password="secret_password",
        )

    second = db_session.exec(select(User).where(User.username == "second_root")).first()
    assert second is None


def test_compose_host_fallback_rewrites_mariadb_to_localhost(monkeypatch):
    monkeypatch.setenv("MARIADB_HOST_PORT", "3307")

    fallback = _compose_host_fallback_db_url(
        "mariadb+mariadbconnector://webapi_user:devepass@mariadb:3306/crud_data"
    )

    assert fallback == "mariadb+mariadbconnector://webapi_user:devepass@127.0.0.1:3307/crud_data"


def test_compose_host_fallback_ignores_non_compose_hosts():
    fallback = _compose_host_fallback_db_url(
        "mariadb+mariadbconnector://webapi_user:devepass@127.0.0.1:3306/crud_data"
    )

    assert fallback is None
