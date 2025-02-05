import os
from dataclasses import dataclass
from typing import List
from .base import getenv
from dotenv import load_dotenv


@dataclass
class TelegramBotConfig:
    token: str
    admins: List[int]

@dataclass
class Config:
    tg_bot: TelegramBotConfig

def load_config() -> Config:
    load_dotenv()

    admins = os.getenv("ADMINS", "")
    admin_ids = [int(admin.strip()) for admin in admins.split(",") if admin.strip().isdigit()]

    return Config(tg_bot=TelegramBotConfig(
        token=getenv("TELEGRAM_TOKEN"),
        admins=admin_ids
    ))