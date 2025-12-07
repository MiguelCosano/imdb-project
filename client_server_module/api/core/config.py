from pydantic_settings import BaseSettings, SettingsConfigDict
from sys import path
from dotenv import load_dotenv
import os

path.append(os.path.realpath("../../"))
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "IMDB API"
    API_DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()