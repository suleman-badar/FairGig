from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    earnings_url: str = 'http://localhost:8002'
    jwt_secret: str = 'change_me'
    jwt_algorithm: str = 'HS256'
    frontend_origin: str = 'http://localhost:5173'


settings = Settings()
