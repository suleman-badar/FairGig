from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = 'fairgig'
    analytics_db_user: str = 'analytics_reader'
    analytics_db_password: str = 'password'

    jwt_secret: str = 'change_me'
    jwt_algorithm: str = 'HS256'

    frontend_origin: str = 'http://localhost:5173'

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.analytics_db_user}:{self.analytics_db_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
