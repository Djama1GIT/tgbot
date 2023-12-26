import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    TOKEN: str = os.getenv('TOKEN')
    CHANNEL_LINK: str = os.getenv('CHANNEL')
    OWNER: int = os.getenv('OWNER')


settings = Settings()
