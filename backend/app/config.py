from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    valkey_url: str = "redis://valkey:6379/0"
    backboard_api_key: str | None = None
    gemini_api_key: str | None = None

settings = Settings()
