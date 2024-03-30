from pydantic import BaseSettings
from functools import lru_cache
from decouple import config

class Settings(BaseSettings):
    env_name : str = config("ENV")
    base_url: str = config("BASE_URL")
    
@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings