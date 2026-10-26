from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project Info
    PROJECT_NAME: str = "LegalFlow AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Ollama Configuration (Local LLM Only)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="llama3.2:latest")

    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./legalflow.db")

    # Storage & RAG Vector Store
    CHROMA_PATH: str = Field(default="./chroma_db")
    STORAGE_PATH: str = Field(default="./storage")
    MAX_UPLOAD_SIZE_MB: int = Field(default=20)

    # Security & Authentication
    JWT_SECRET: str = Field(default="legalflow_super_secret_jwt_key_314159265358979323846")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "*"])

    # Services Configuration
    OCR_ENGINE: str = Field(default="tesseract")
    EMBEDDING_MODEL: str = Field(default="nomic-embed-text")
    LOG_LEVEL: str = Field(default="INFO")

settings = Settings()
