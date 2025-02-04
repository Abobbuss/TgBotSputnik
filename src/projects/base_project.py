import os
from pathlib import Path

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class BaseProject:

    BASE_DIR = Path(__file__).parent / "presentations"  # Путь к папке с презентациями

    def __init__(self, name: str, tg_link: str, description: str, folder_presentation_name: str):
        self.name = name
        self.tg_link = tg_link
        self.description = description
        self.presentation_path = self.BASE_DIR / folder_presentation_name.lower()

    def get_info(self) -> str:
        return f"📌 <b>{self.name}</b>\n\n🔗 <a href='{self.tg_link}'>Telegram</a>\n\nℹ️ {self.description}"

    def get_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📄 Получить презентацию", callback_data=f"presentation_{self.name.lower()}")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_projects")]
        ])

    def get_presentation(self) -> Path | None:
        """Возвращает путь к презентации, если она есть."""

        if self.presentation_path.exists() and self.presentation_path.is_dir():
            files = list(self.presentation_path.glob("*.pptx"))
            return files[0] if files else None

        return None
