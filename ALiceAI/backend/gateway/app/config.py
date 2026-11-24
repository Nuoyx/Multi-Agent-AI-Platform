from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    auth_service_url: str = "http://127.0.0.1:8081"
    frontend_url: str = "http://localhost:5173"


settings = Settings()
