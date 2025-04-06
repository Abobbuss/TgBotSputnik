from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import load_config

config = load_config()

class InlineKeyboards:
    @staticmethod
    def start_menu(user_id: int):
        buttons = [
            [InlineKeyboardButton(text="📄 Получить материалы круглого стола", callback_data="get_materials")],
            [InlineKeyboardButton(text="🔍 В каком направлении вы работаете?", callback_data="select_direction")],
        ]

        if user_id in config.tg_bot.admins:
            buttons.append([
                InlineKeyboardButton(text="🧾 Сгенерировать QR", callback_data="generate_qr")
            ])
            buttons.append([
                InlineKeyboardButton(text="📁 Показать все QR", callback_data="show_all_qr")
            ])
            buttons.append([
                InlineKeyboardButton(text="👥 Всего пользователей", callback_data="show_user_count")
            ])
            buttons.append([
                InlineKeyboardButton(text="📊 Рефералы", callback_data="show_referrals")
            ])
            buttons.append([
                InlineKeyboardButton(text="🗂 Запросы пользователей", callback_data="show_user_requests")
            ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def direction_selection():
        buttons = [
            [InlineKeyboardButton(text="🟠 Руды", callback_data="choose_ruda")],
            [InlineKeyboardButton(text="⚫ Уголь", callback_data="choose_ugol")],
            [InlineKeyboardButton(text="🟢 Работаю в обоих направлениях", callback_data="choose_both")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def project_options_keyboard(project_type: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ Узнать подробнее", callback_data=f"{project_type}_details")],
            [InlineKeyboardButton(text="📝 Записаться на демо", callback_data=f"{project_type}_demo")],
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
