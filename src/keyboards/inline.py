from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import load_config

config = load_config()

class InlineKeyboards:
    @staticmethod
    def start_menu(user_id: int):
        buttons = [
            [InlineKeyboardButton(text="📄 Получить материалы круглого стола", callback_data="get_materials")],
            [InlineKeyboardButton(text="🔍 Узнать подробнее о продукте", callback_data="select_direction")],
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
            [InlineKeyboardButton(text="🟠 Руда", callback_data="choose_ruda")],
            [InlineKeyboardButton(text="⚫ Уголь", callback_data="choose_ugol")],
            [InlineKeyboardButton(text="🟢 Работаю в обоих направлениях", callback_data="choose_both")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_main_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def project_options_keyboard(project_type: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ Узнать подробнее", callback_data=f"{project_type}_details")],
            [InlineKeyboardButton(text="📝 Записаться на демо", callback_data=f"{project_type}_demo")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="select_direction")]
        ])

    @staticmethod
    def cancel():
        buttons = [
            [InlineKeyboardButton(text="⬅ Отмена", callback_data="back_to_main_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_video_round_table():
        buttons = [
            [InlineKeyboardButton(text="🎥 Получить записи круглого стола", callback_data="get_video_to_round_table")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_main_menu")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def phone_request_keyboard() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="📲 Поделиться номером", request_contact=True),
                    KeyboardButton(text="❌ Отмена")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )