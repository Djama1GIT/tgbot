import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    TOKEN: str = os.getenv('TOKEN')
    OWNER: int = os.getenv('OWNER')

    CHANNEL_LINK: str = os.getenv('CHANNEL_LINK')
    LINK_TEXT: str = os.getenv("LINK_TEXT")

    WELCOME_MESSAGE: str = os.getenv("WELCOME_MESSAGE")


settings = Settings()
