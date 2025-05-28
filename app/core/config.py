from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "FDA DB Checkup"
    VERSION: str = "0.1.0"

    # Database settings - individual components
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    DATABASE_URL: Optional[str] = None

    # FDA base URL
    FDA_BASE_URL: str = "https://api.fda.gov/device/event.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        """Construct DATABASE_URL from individual components if not provided directly."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Create settings instance
settings = Settings()
