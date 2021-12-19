from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "DEBUG"

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 27017
    DB_NAME: str
    AUTH_DB_NAME: Optional[str]

    WEB_HOST: str = "0.0.0.0"
    WEB_PORT: int = 8080

    MANAGEMENT_API_URL: str
    MANAGEMENT_API_PORT: int

    class Config:
        env_prefix = "BANTER_BUS_CORE_API_"
        env_file = ".env"

    def get_mongodb_uri(self) -> str:
        uri = f"mongodb://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}"
        if self.AUTH_DB_NAME:
            uri += f"?authSource={self.AUTH_DB_NAME}"

        return uri

    def get_management_url(self) -> str:
        management_api_base = self.MANAGEMENT_API_URL
        if self.MANAGEMENT_API_PORT:
            management_api_base += f":{self.MANAGEMENT_API_PORT}"

        return management_api_base


@lru_cache()
def get_settings():
    print("HERE")
    return Settings()
