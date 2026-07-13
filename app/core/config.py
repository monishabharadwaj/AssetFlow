from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ML_ROOT = Path(__file__).resolve().parents[2] / "ml" / "artifacts"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "AssetFlow AI"
    debug: bool = False
    database_url: str = "postgresql://postgres:postgres@localhost:5432/assetflow_ai"

    ml_enabled: bool = True
    ml_model_path: str = str(_ML_ROOT / "model.pt")
    ml_feature_stats_path: str = str(_ML_ROOT / "feature_stats.json")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: float = 30.0
    assistant_enabled: bool = True
    assistant_use_ollama: bool = True

    drift_min_drop: float = 0.10
    drift_severe_drop: float = 0.15
    drift_healthy_floor: float = 0.75
    drift_notify_below: float = 0.60

    policy_automation_enabled: bool = True
    scheduler_enabled: bool = False
    scheduler_interval_minutes: int = 60
    scheduler_run_on_startup: bool = False

    auth_enabled: bool = True
    jwt_secret_key: str = "change-me-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # Comma-separated browser origins allowed by CORS (local Vite defaults).
    # Production (Option A): set CORS_ORIGINS=http://YOUR_EC2_PUBLIC_IP
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:3000,http://127.0.0.1:3000"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
