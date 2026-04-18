from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anomaly_service_port: int = 8003
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
