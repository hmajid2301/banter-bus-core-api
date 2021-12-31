from functools import lru_cache
from typing import Optional

from omnibus.config.settings import OmnibusSettings


class Settings(OmnibusSettings):
    MANAGEMENT_API_URL: str
    MANAGEMENT_API_PORT: Optional[int]

    class Config:
        env_prefix = "BANTER_BUS_CORE_API_"
        env_file = ".env"

    def get_management_url(self) -> str:
        management_api_base = self.MANAGEMENT_API_URL
        if self.MANAGEMENT_API_PORT:
            management_api_base += f":{self.MANAGEMENT_API_PORT}"

        return management_api_base


@lru_cache()
def get_settings():
    return Settings()
