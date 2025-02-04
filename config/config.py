from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

from .base import getenv, ImproperlyConfigured


@dataclass
class TelegramBotConfig:
    token: str

@dataclass
class Config:
    tg_bot: TelegramBotConfig

def load_config() -> Config:
    load_dotenv()

    return Config(tg_bot=TelegramBotConfig(
        token=getenv("TELEGRAM_TOKEN"),
    ))