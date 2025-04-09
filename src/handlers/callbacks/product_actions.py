from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from src.constants import message_constants
from src.keyboards.inline import InlineKeyboards
from src.states.states import UserState
from src.models.db import Database
from config import load_config

config = load_config()
manager_id = config.tg_bot.manager_id

router = Router()


async def notify_manager_about_demo(bot: Bot, db: Database, message: Message, project_name: str):
    """
    Уведомляет менеджера о новой записи на демо по проекту.
    """
    user = db.get_user(message.from_user.id)
    username = user[2] or "Неизвестно"
    phone = user[3] or "Не указан"
    full_info = user[4] or "Нет дополнительной информации"

    text = (
        f"📌 <b>Новая запись на демо</b>\n"
        f"Проект: <b>{project_name}</b>\n"
        f"Пользователь: @{username} (ID: {message.from_user.id})\n"
        f"Дата: <i>{message.date.strftime('%d.%m.%Y %H:%M')}</i>\n\n"
        f"📞 Телефон: <code>{phone}</code>\n"
        f"📝 Доп информация о пользователе:\n{full_info}"
    )

    await bot.send_message(chat_id=config.tg_bot.manager_id, text=text)

# === RUDA ===

@router.callback_query(F.data == "ruda_details")
async def ruda_details(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_EMAIL_RUDA)
    await callback.message.answer("📧 Напишите свой email: мы пришлем вам запись выступлений Круглого стола.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "ruda_demo")
async def ruda_demo(callback: CallbackQuery, state: FSMContext, db: Database):
    if db.has_phone(callback.from_user.id):
        await state.set_state(UserState.CONFIRM_PHONE_RUDA)
        await callback.message.answer(
            "📱 У вас уже указан номер телефона. Хотите заменить его?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да", callback_data="ruda_phone_yes")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="ruda_phone_no")],
                [InlineKeyboardButton(text="⬅ Отмена", callback_data="back_to_main_menu")],
            ])
        )
    else:
        await state.set_state(UserState.AWAITING_PHONE_RUDA)
        await callback.message.answer("📱 Укажите ваш номер телефона.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "ruda_phone_yes")
async def ruda_phone_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_PHONE_RUDA)
    await callback.message.answer("📱 Введите новый номер телефона.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "ruda_phone_no")
async def ruda_phone_no(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_CONTACT_INFO_RUDA)
    await callback.message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\n"
        "Пожалуйста, напишите контакную информацию <b>одним сообщением</b>",
        reply_markup=InlineKeyboards.cancel()
    )
    await callback.answer()

@router.message(UserState.AWAITING_PHONE_RUDA)
async def handle_ruda_phone(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, phone=message.text.strip())
    await state.set_state(UserState.AWAITING_CONTACT_INFO_RUDA)
    await message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\n"
        "Пожалуйста, напишите контакную информацию <b>одним сообщением</b>",
        reply_markup=InlineKeyboards.cancel()
    )

@router.message(UserState.AWAITING_EMAIL_RUDA)
async def handle_ruda_email(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, info=message.text)
    db.add_user_action(message.from_user.id, "Запрос записи круглого стола (руда)")

    await message.answer("✅ Спасибо! Видео будет отправлено на указанную почту.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer("<b>Главное меню</b>, выберите действие.", reply_markup=InlineKeyboards.start_menu(message.from_user.id))
    await state.clear()

@router.message(UserState.AWAITING_CONTACT_INFO_RUDA)
async def handle_ruda_contact(message: Message, state: FSMContext, db: Database, bot: Bot):
    info = message.text.strip()
    db.update_user_info(message.from_user.id, info=info)
    db.add_user_action(message.from_user.id, "Запись на демо (руда)")

    await state.set_state(UserState.MAIN_MENU)
    await message.answer("✅ Спасибо! Запись на демо зафиксирована.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer("<b>Главное меню</b>, выберите действие.", reply_markup=InlineKeyboards.start_menu(message.from_user.id))

    await notify_manager_about_demo(bot, db, message, "Руда")

@router.callback_query(F.data == "ruda_share")
async def handle_ruda_share(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await callback.message.answer(message_constants.SOCIAL_TEXT)
    await state.clear()
    await callback.answer()



# === UGOL ===

@router.callback_query(F.data == "ugol_details")
async def ugol_details(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_EMAIL_UGOL)
    await callback.message.answer("📧 Напишите свой email: мы пришлем вам запись выступлений Круглого стола.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "ugol_demo")
async def ugol_demo(callback: CallbackQuery, state: FSMContext, db: Database):
    if db.has_phone(callback.from_user.id):
        await state.set_state(UserState.CONFIRM_PHONE_UGOL)
        await callback.message.answer(
            "📱 У вас уже указан номер телефона. Хотите заменить его?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да", callback_data="ugol_phone_yes")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="ugol_phone_no")],
                [InlineKeyboardButton(text="⬅ Отмена", callback_data="back_to_main_menu")],
            ])
        )
    else:
        await state.set_state(UserState.AWAITING_PHONE_UGOL)
        await callback.message.answer("📱 Укажите ваш номер телефона.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "ugol_phone_yes")
async def ugol_phone_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_PHONE_UGOL)
    await callback.message.answer("📱 Введите новый номер телефона.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "ugol_phone_no")
async def ugol_phone_no(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_CONTACT_INFO_UGOL)
    await callback.message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\n"
        "Пожалуйста, напишите контакную информацию <b>одним сообщением</b>\n"
        "Мы свяжемся с вами в течение 24 часов для уточнения деталей.",
        reply_markup=InlineKeyboards.cancel()
    )
    await callback.answer()

@router.message(UserState.AWAITING_PHONE_UGOL)
async def handle_ugol_phone(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, phone=message.text.strip())
    await state.set_state(UserState.AWAITING_CONTACT_INFO_UGOL)
    await message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\n"
        "Пожалуйста, напишите контакную информацию <b>одним сообщением</b>\n"
        "Мы свяжемся с вами в течение 24 часов для уточнения деталей.",
        reply_markup=InlineKeyboards.cancel()
    )

@router.message(UserState.AWAITING_EMAIL_UGOL)
async def handle_ugol_email(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, info=message.text)
    db.add_user_action(message.from_user.id, "Запрос записи круглого стола (уголь)")

    await message.answer("✅ Спасибо! Видео будет отправлено на указанную почту.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer("<b>Главное меню</b>, выберите действие.", reply_markup=InlineKeyboards.start_menu(message.from_user.id))
    await state.clear()

@router.message(UserState.AWAITING_CONTACT_INFO_UGOL)
async def handle_ugol_contact(message: Message, state: FSMContext, db: Database, bot: Bot):
    info = message.text.strip()
    db.update_user_info(message.from_user.id, info=info)
    db.add_user_action(message.from_user.id, "Запись на демо (уголь)")

    await state.set_state(UserState.MAIN_MENU)
    await message.answer("✅ Спасибо! Запись на демо зафиксирована.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS)
    await message.answer("<b>Главное меню</b>, выберите действие.", reply_markup=InlineKeyboards.start_menu(message.from_user.id))
    await state.clear()

    await notify_manager_about_demo(bot, db, message, "Уголь")

@router.callback_query(F.data == "ugol_share")
async def handle_ugol_share(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await callback.message.answer(message_constants.SOCIAL_TEXT)
    await state.clear()
    await callback.answer()


# === BOTH ===


@router.callback_query(F.data == "both_details")
async def both_details(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_EMAIL_BOTH)
    await callback.message.answer("📧 Напишите свой email: мы пришлем вам запись выступлений Круглого стола.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.message(UserState.AWAITING_EMAIL_BOTH)
async def handle_both_email(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, info=message.text)
    db.add_user_action(message.from_user.id, "Запрос записи круглого стола (руда и уголь)")

    await message.answer("✅ Спасибо! Видео будет отправлено на указанную почту.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer("<b>Главное меню</b>, выберите действие.", reply_markup=InlineKeyboards.start_menu(message.from_user.id))
    await state.clear()

@router.callback_query(F.data == "both_demo")
async def both_demo(callback: CallbackQuery, state: FSMContext, db: Database):
    if db.has_phone(callback.from_user.id):
        await state.set_state(UserState.CONFIRM_PHONE_BOTH)
        await callback.message.answer(
            "📱 У вас уже указан номер телефона. Хотите заменить его?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да", callback_data="both_phone_yes")],
                [InlineKeyboardButton(text="❌ Нет", callback_data="both_phone_no")],
                [InlineKeyboardButton(text="⬅ Отмена", callback_data="back_to_main_menu")],
            ])
        )
    else:
        await state.set_state(UserState.AWAITING_PHONE_BOTH)
        await callback.message.answer("📱 Укажите ваш номер телефона.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "both_phone_yes")
async def both_phone_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_PHONE_BOTH)
    await callback.message.answer("📱 Введите новый номер телефона.", reply_markup=InlineKeyboards.cancel())
    await callback.answer()

@router.callback_query(F.data == "both_phone_no")
async def both_phone_no(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_CONTACT_INFO_BOTH)
    await callback.message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\nПожалуйста, напишите контакную информацию <b>одним сообщением</b>",
        reply_markup=InlineKeyboards.cancel()
    )
    await callback.answer()

@router.message(UserState.AWAITING_PHONE_BOTH)
async def handle_both_phone(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, phone=message.text.strip())
    await state.set_state(UserState.AWAITING_CONTACT_INFO_BOTH)
    await message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\nПожалуйста, напишите контакную информацию <b>одним сообщением</b>",
        reply_markup=InlineKeyboards.cancel()
    )

@router.message(UserState.AWAITING_CONTACT_INFO_BOTH)
async def handle_both_contact(message: Message, state: FSMContext, db: Database, bot: Bot):
    info = message.text.strip()
    db.update_user_info(message.from_user.id, info=info)
    db.add_user_action(message.from_user.id, "Запись на демо (руда и уголь)")

    await state.set_state(UserState.MAIN_MENU)
    await message.answer("✅ Спасибо! Запись на демо зафиксирована.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer("<b>Главное меню</b>, выберите действие.", reply_markup=InlineKeyboards.start_menu(message.from_user.id))

    await notify_manager_about_demo(bot, db, message, "Уголь и Руда")