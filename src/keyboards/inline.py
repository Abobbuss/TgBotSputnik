from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class InlineKeyboards:
    @staticmethod
    def main_menu():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Наши проекты", callback_data="projects")],
            [InlineKeyboardButton(text="Новости спутника", callback_data="news")],
            [InlineKeyboardButton(text="Получить презентацию", callback_data="presentation")],
            [InlineKeyboardButton(text="Хочу инвестировать", callback_data="invest")],
            [InlineKeyboardButton(text="Хочу открыть стартап", callback_data="startup")]
        ])

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
    def news_menu():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_main")]
        ])
