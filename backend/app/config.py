from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    github_token: str = ""
    database_url: str = "sqlite:///./data/archaeologist.db"
    ollama_api_url: str = "http://ollama:11434"
    llm_model: str = "llama3:latest"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
