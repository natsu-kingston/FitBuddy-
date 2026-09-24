from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    debug: bool = True

    gemini_api_key: str = ""
    workout_model: str = "gemini-3.1-pro-preview"
    tip_model: str = "gemini-3.8-flash"
    demo_mode: bool = False

    database_url: str = "sqlite:///./fitbuddy.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def gemini_enabled(self) -> bool:
        return bool(self.gemini_api_key.strip()) and not self.demo_mode


@lru_cache
def get_settings() -> Settings:
    return Settings()
