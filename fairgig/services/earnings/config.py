from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "fairgig"
    postgres_user: str = "fairgig_admin"
    postgres_password: str = "your_strong_password_here"

    jwt_secret: str = "change_me_to_a_long_secret"
    jwt_algorithm: str = "HS256"

    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_mime_types: str = "image/jpeg,image/png,image/webp"

    frontend_origin: str = "http://localhost:5173"

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
