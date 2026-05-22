from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    environment: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"  # ignora variables del .env no definidas en Settings (POSTGRES_USER, etc)


settings = Settings()