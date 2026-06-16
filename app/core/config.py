from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "AssetFlow AI"
    debug: bool = False
    database_url: str = "postgresql://postgres:postgres@localhost:5432/assetflow_ai"


settings = Settings()
