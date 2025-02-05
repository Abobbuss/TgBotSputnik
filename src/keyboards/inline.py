from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import load_config

config = load_config()

class InlineKeyboards:
    @staticmethod
    def main_menu(user_id: int):
        buttons = [
            [InlineKeyboardButton(text="Наши проекты", callback_data="projects")],
            [InlineKeyboardButton(text="Новости спутника", callback_data="news")],
            [InlineKeyboardButton(text="Получить презентацию", callback_data="presentation")],
        ]

        if user_id in config.tg_bot.admins:
            buttons.append(
                [InlineKeyboardButton(text="Загрузить последнюю презентацию", callback_data="upload_presentation")])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def projects_menu():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ГЕОС", callback_data="geos")],
            [InlineKeyboardButton(text="Ферма", callback_data="farm")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_main")]
        ])

    @staticmethod
    def project_buttons(project_name: str):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📄 Получить презентацию", callback_data=f"presentation_{project_name.lower()}")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="projects")]
        ])

    @staticmethod
    def back_to_main():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_main")]
        ])

    @staticmethod
    def news_navigation(index: int, total: int,  user_id: int):
        buttons = []

        if index > 0:
            buttons.append(InlineKeyboardButton(text="⬅ Предыдущая", callback_data=f"news_{index - 1}"))
        if index < total - 1:
            buttons.append(InlineKeyboardButton(text="Следующая ➡", callback_data=f"news_{index + 1}"))

        buttons.append(InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_main"))

        if user_id in config.tg_bot.admins:
            buttons.append(InlineKeyboardButton(text="➕ Добавить новость", callback_data="add_news"))

        return InlineKeyboardMarkup(inline_keyboard=[buttons])
