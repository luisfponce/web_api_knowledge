from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import EmailStr

class Settings(BaseSettings):
    MAIL_USERNAME: str = Field("test@example.com", env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field("password", env="MAIL_PASSWORD")
    MAIL_FROM: EmailStr = Field("noreply@example.com", env="MAIL_FROM")