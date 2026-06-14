"""Application configuration."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="ScholarFlow AI", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    backend_host: str = Field(default="127.0.0.1", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")

    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/scholarflow",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(default="change-this-secret", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=1440,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    upload_dir: str = Field(default="./uploads", alias="UPLOAD_DIR")
    chroma_persist_dir: str = Field(
        default="./storage/chroma",
        alias="CHROMA_PERSIST_DIR",
    )
    embedding_model_name: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL_NAME",
    )
    text_chunk_size: int = Field(default=1000, alias="TEXT_CHUNK_SIZE")
    text_chunk_overlap: int = Field(default=200, alias="TEXT_CHUNK_OVERLAP")
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("text_chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("TEXT_CHUNK_SIZE must be greater than 0")
        return value

    @field_validator("text_chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, value: int) -> int:
        if value < 0:
            raise ValueError("TEXT_CHUNK_OVERLAP cannot be negative")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
