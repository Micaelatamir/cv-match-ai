from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # lê do .env ou das variáveis de ambiente
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CV Match AI"
    database_url: str = "postgresql+psycopg://cvmatch:cvmatch@localhost:5432/cvmatch"

    # LLM é opcional, sem chave a API usa as sugestões por regra
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 30.0


settings = Settings()
