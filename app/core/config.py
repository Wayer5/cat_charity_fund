from typing import Optional

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_title = 'Кошачий благотворительный фонд.'
    description = 'Сервис для поддержки котиков!'
    version: str = '0.1.0'
    database_url: str = 'sqlite+aiosqlite:///./qrcat.db'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
