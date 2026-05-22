from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    environment: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"  # suppress warnings for undeclared vars like POSTGRES_USER


settings = Settings()