from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "json"
    github_token: str = ""
    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./data/archaeologist.db"
    ollama_api_url: str = "http://ollama:11434"
    llm_model: str = "llama3:latest"
    queue_type: str = "memory"
    cache_dir: str = "./data/cache"
    cache_ttl: int = 86400
    max_workers: int = 4
    max_commit_depth: int = 500
    webhook_timeout: int = 30
    analysis_timeout: int = 300
    enable_llm_analysis: bool = False
    enable_webhooks: bool = True
    enable_background_jobs: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
