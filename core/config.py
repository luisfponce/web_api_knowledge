from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

# SMTP server configuration
smtp_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('ENV_MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('ENV_MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('ENV_MAIL_USERNAME'),
    MAIL_FROM_NAME="Your App",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)