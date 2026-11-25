from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    auth_service_url: str = "http://127.0.0.1:8081"
    frontend_url: str = "http://localhost:5173"
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST"]
    cors_allow_headers: list[str] = ["Content-Type"]
    redis_url: SecretStr = SecretStr("redis://127.0.0.1:6379/0")


settings = Settings()
