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
    assistant_use_ollama: bool = False


settings = Settings()
