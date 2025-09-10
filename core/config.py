from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
import os
from schemas.email_schema import Settings

load_dotenv()

settings = Settings()

# SMTP server configuration
smtp_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME="Your App",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# JWT configuration
JWT_SECRET_KEY = os.getenv("ENV_SECRET_KEY", "testkey")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Redis configuration
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PSW = None
REDIS_DECODE_RESP = True

# MariaDB server
# Ensure that the environment variable DB_URL is set to your MariaDB connection string
# Example: export DB_URL="mariadb+mariadbconnector://user:psw@127.0.0.1:3306/bank_db"

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    DB_URL = "sqlite:///./bank_db.db"  # Default to SQLite if no environment variable is set