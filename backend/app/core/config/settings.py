import os

from pathlib import Path
from pydantic_settings import BaseSettings


BASE_PATH = Path(__file__).resolve().parent.parent.parent.parent
LOG_PATH = os.path.join(BASE_PATH, 'logs')


class Settings(BaseSettings):

    # FastAPI
    API_V1_STR: str = '/api/v1'
    TITLE: str = 'Gpt Service'
    VERSION: str = '0.1'
    DESCRIPTION: str = 'Gpt Service API'
    DOCS_URL: str | None = f'/docs'
    REDOCS_URL: str | None = f'/redocs'
    DEBUG: bool

    # Log
    LOG_FILENAME: str = 'gpt_service.log'


settings = Settings(DEBUG=True)
