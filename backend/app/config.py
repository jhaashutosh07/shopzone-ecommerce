from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Return Policy Engine"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/return_engine"

    # JWT Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Key Settings
    api_key_prefix: str = "rpe_"

    # ML Model
    model_path: str = "ml/models/scoring_model.joblib"
    bootstrap_train: bool = True  # train an initial model on startup if none exists

    # Scoring thresholds
    high_risk_threshold: float = 30.0
    medium_risk_threshold: float = 60.0

    # Demo merchant auto-provisioning (used by docker compose demo)
    demo_merchant_email: str = ""
    demo_merchant_password: str = "demo1234"
    demo_merchant_name: str = "ShopZone Demo Store"
    demo_api_key: str = ""

    # CORS (comma-separated origins)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
