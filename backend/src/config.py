"""Application configuration using pydantic-settings."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    database_url: str = "sqlite:///./todo.db"

    # Application
    app_name: str = "Todo Backend API"
    debug: bool = False
    environment: str = "development"

    # Server (PORT is set by Railway automatically)
    api_host: str = "0.0.0.0"
    api_port: int = int(os.environ.get("PORT", 8000))

    # CORS (comma-separated origins, supports wildcards for dev)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Logging
    log_level: str = "INFO"

    # JWT Authentication
    jwt_secret: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 7
    jwt_issuer: str = "todo-backend-api"
    jwt_audience: str = "todo-frontend"

    # Security
    bcrypt_rounds: int = 12  # Use 4 for development, 12+ for production

    # LLM Configuration (defaults to Groq free tier)
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
