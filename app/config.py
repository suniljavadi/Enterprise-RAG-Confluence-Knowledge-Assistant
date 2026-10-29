from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./enterprise_rag.db"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    mock_llm: bool = True
    api_auth_token: str | None = None
    log_level: str = "INFO"
    top_k: int = 8
    cors_origins: str = "http://localhost:8501"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_for_runtime(self) -> None:
        if self.app_env.lower() != "production":
            return
        problems = []
        if not self.api_auth_token or self.api_auth_token == "portfolio-demo-token":
            problems.append("API_AUTH_TOKEN must be set to a non-demo value")
        if self.database_url.startswith("sqlite"):
            problems.append("DATABASE_URL must not be SQLite")
        if "*" in self.cors_origin_list:
            problems.append("CORS_ORIGINS must not contain '*'")
        if problems:
            raise RuntimeError("Unsafe production configuration: " + "; ".join(problems))


@lru_cache
def get_settings() -> Settings:
    return Settings()
