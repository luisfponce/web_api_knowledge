PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 1024

PASSWORD_REQUIREMENTS_MESSAGE = "Password does not meet the requirements"
PASSWORD_MIN_LENGTH_MESSAGE = f"Password must be at least {PASSWORD_MIN_LENGTH} characters"

COMMON_PASSWORDS = {
    "password",
    "password123",
    "password1234",
    "123456789012",
    "qwerty123456",
    "adminadmin123",
    "letmein123456",
    "welcome12345",
}


def is_common_password(password: str) -> bool:
    return password.strip().lower() in COMMON_PASSWORDS


def validate_password_strength(password: str) -> str:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(PASSWORD_MIN_LENGTH_MESSAGE)
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
    if is_common_password(password):
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
    return password
