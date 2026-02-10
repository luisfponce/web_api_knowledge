from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import EmailStr

class Settings(BaseSettings):
    ENV_MAIL_USERNAME: str = Field("test@example.com", env="ENV_MAIL_USERNAME")
    ENV_MAIL_PASSWORD: str = Field("password", env="ENV_MAIL_PASSWORD")
    ENV_MAIL_FROM: EmailStr = Field("test@example.com", env="ENV_MAIL_USERNAME")