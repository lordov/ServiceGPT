import os
import openai
from pathlib import Path
from pydantic_settings import BaseSettings
from environs import Env

env = Env()
env.read_env()


BASE_PATH = Path(__file__).resolve().parent.parent.parent.parent
LOG_PATH = os.path.join(BASE_PATH, 'logs')


class Settings(BaseSettings):
    # Database
    DB_USER: str = env.str("DB_USER", "root")
    DB_PASSWORD: str = env.str("DB_PASSWORD", "password")
    DB_HOST: str = env.str("DB_HOST", "localhost")
    DB_NAME: str = env.str("DB_NAME", "chatgpt_db")
    DB_PORT: str | int = env.str("DB_PORT", "3306")
    TEST_DB_NAME: str = os.getenv("TEST_DB_NAME", "test_chatgpt_db")

    DATABASE_URL: str = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    
    TEST_DATABASE_URL: str = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

    # JWT
    SECRET_KEY: str = env.str("SECRET_KEY", "your_secret_key")
    # OpenAI
    GPT_API_KEY: str = os.getenv("GPT_API_KEY")
    GPT_URL: str = os.getenv("GPT_URL")
    
    # FastAPI
    API_V1_STR: str = '/api/v1'
    TITLE: str = 'Gpt Service'
    VERSION: str = '0.1'
    DESCRIPTION: str = 'Gpt Service API'
    DOCS_URL: str | None = f'/docs'
    REDOCS_URL: str | None = f'/redocs'
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    # Logging
    LOG_FILENAME: str = os.getenv("LOG_FILENAME", "gpt_service.log")


settings = Settings(DEBUG=True)
