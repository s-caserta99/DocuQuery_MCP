from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env."""

    app_name: str = "DocuQuery MCP"
    debug: bool = False

    documents_path: str = "./documents"
    vector_store_path: str = "./vector_store"

    embedding_model: str = "all-MiniLM-L6-v2"

    max_chunk_size: int = 800
    chunk_overlap: int = 100

    port: int = 8001
    host: str = "0.0.0.0"

    log_level: str = "INFO"

    mcp_auth_token: str = ""          

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()