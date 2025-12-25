from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ecommerce_db"

    # JWT
    secret_key: str = "ecommerce-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Return Policy Engine Integration
    return_engine_url: str = "http://localhost:8000/api/v1"
    return_engine_api_key: str = ""

    # App settings
    app_name: str = "ShopZone E-commerce"
    api_prefix: str = "/api/v1"

    @field_validator('database_url', mode='before')
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        # Render uses postgres:// but SQLAlchemy needs postgresql://
        if v and v.startswith('postgres://'):
            return v.replace('postgres://', 'postgresql://', 1)
        return v

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
