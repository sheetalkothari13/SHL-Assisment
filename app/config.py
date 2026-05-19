from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    app_title: str = "SHL Assessment Recommender"
    app_description: str = "Conversational agent and dashboard for SHL assessment selection"
    app_version: str = "1.1.0"
    database_url: str = "sqlite+aiosqlite:///./shl_assessment.db"
    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
