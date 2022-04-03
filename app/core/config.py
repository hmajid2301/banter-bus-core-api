from functools import lru_cache
from typing import Optional

from omnibus.config.settings import OmnibusSettings


class Settings(OmnibusSettings):
    MANAGEMENT_API_URL: str
    MANAGEMENT_API_PORT: Optional[int]
    DISCONNECT_TIMER_IN_SECONDS: int = 300

    MESSAGE_QUEUE_HOST: str
    MESSAGE_QUEUE_PORT: Optional[int]

    QUESTIONS_PER_ROUND: int = 3

    class Config:
        env_prefix = "BANTER_BUS_CORE_API_"
        env_file = ".env"

    def get_management_url(self) -> str:
        management_api_base = self.MANAGEMENT_API_URL
        if self.MANAGEMENT_API_PORT:
            management_api_base += f":{self.MANAGEMENT_API_PORT}"

        return management_api_base

    def get_redis_uri(self) -> str:
        uri = f"redis://{self.MESSAGE_QUEUE_HOST}"
        if self.MESSAGE_QUEUE_PORT:
            uri += f":{self.MESSAGE_QUEUE_PORT}"

        return uri


@lru_cache()
def get_settings():
    return Settings()
