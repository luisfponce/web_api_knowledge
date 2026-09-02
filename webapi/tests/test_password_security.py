import pytest
from passlib.hash import sha256_crypt

from auth.password_service import hash_password, password_hash_needs_update, verify_password
from core.password_policy import validate_password_strength


def test_password_policy_accepts_valid_password():
    assert validate_password_strength("correct-horse-demo") == "correct-horse-demo"


def test_password_policy_rejects_short_password():
    with pytest.raises(ValueError, match="at least 6 characters"):
        validate_password_strength("short")


def test_password_policy_rejects_common_password():
    with pytest.raises(ValueError, match="does not meet"):
        validate_password_strength("password1234")


def test_hash_password_uses_argon2id_and_verifies():
    password_hash = hash_password("correct-horse-demo")

    assert password_hash.startswith("$argon2id$")
    assert verify_password("correct-horse-demo", password_hash)
    assert not password_hash_needs_update(password_hash)


def test_verify_password_supports_legacy_sha256_hashes():
    password_hash = sha256_crypt.hash("legacy_password")

    assert verify_password("legacy_password", password_hash)
    assert password_hash_needs_update(password_hash)
