# thirdparty
from pydantic import BaseSettings, Field


class TelegramSettings(BaseSettings):
    token: str = Field(env="TELEGRAM_TOKEN")


tg_settings = TelegramSettings()
