from typing import Optional

from pydantic import BaseSettings, EmailStr, PostgresDsn


class Settings(BaseSettings):
    app_title: str = 'Файловый дескриптор'
    database_dsn: PostgresDsn
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = 'user@example.com'
    first_superuser_password: Optional[str] = '1234566789987654321'

    class Config:
        env_file = '.env'


settings = Settings()
