from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext

from src.constants import message_constants
from src.keyboards.inline import InlineKeyboards
from src.states.states import UserState
from src.models.db import Database
from config import load_config

from pathlib import Path


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
    last_info = db.get_last_demo_info(message.from_user.id) or "Нет дополнительной информации"

    text = (
        f"📌 <b>Новая запись на демо</b>\n"
        f"Проект: <b>{project_name}</b>\n"
        f"Пользователь: @{username} (ID: {message.from_user.id})\n"
        f"Дата: <i>{message.date.strftime('%d.%m.%Y %H:%M')}</i>\n\n"
        f"📞 Телефон: <code>{phone}</code>\n"
        f"📝 Доп информация о пользователе:\n{last_info}"
    )

    await bot.send_message(chat_id=config.tg_bot.manager_id, text=text)


async def send_project_files(callback: CallbackQuery, folder_name: str):
    """
    Отправляет все файлы из указанной папки проекта.
    """
    folder_path = Path(__file__).parent.parent.parent / "files" / folder_name

    project_titles = {
        "ruda": "Руда",
        "ugol": "Уголь",
        "both": "Руда и Уголь"
    }

    readable_name = project_titles.get(folder_name.lower(), folder_name.title())

    if not folder_path.exists() or not folder_path.is_dir():
        await callback.message.answer(f"❌ Произошла ошибка, попробуйте позже.")
        return

    files = list(folder_path.glob("*.*"))
    if not files:
        await callback.message.answer(f"❌ Нет файлов для проекта.")
        return

    await callback.message.answer(f"📂 Материалы по проекту <b>{readable_name}</b>:")

    for file_path in files:
        try:
            file = FSInputFile(file_path)
            await callback.message.answer_document(file)
        except Exception:
            await callback.message.answer("⚠️ Не удалось отправить один из файлов.")


async def handle_project_details(callback: CallbackQuery, folder_names: list[str], project_code: str):
    """
    Отправляет материалы по проекту, соцсети и возвращает кнопки выбора.
    """
    for folder in folder_names:
        await send_project_files(callback, folder)

    await callback.message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await callback.message.answer(message_constants.SOCIAL_TEXT)

    project_titles = {
        "ruda": "Руда",
        "ugol": "Уголь",
        "both": "Руда и Уголь"
    }

    readable_name = project_titles.get(project_code.lower(), project_code.title())

    await callback.message.answer(
        f"Выберите действие по проекту: <b>{readable_name}</b>",
        reply_markup=InlineKeyboards.project_options_keyboard(project_code)
    )

    await callback.answer()

# === RUDA ===

@router.callback_query(F.data == "ruda_details")
async def ruda_details(callback: CallbackQuery, state: FSMContext):
    await handle_project_details(callback, ["ruda"], "ruda")

@router.callback_query(F.data == "ruda_demo")
async def ruda_demo(callback: CallbackQuery, state: FSMContext, db: Database):
    if db.has_phone(callback.from_user.id):
        await state.set_state(UserState.CONFIRM_PHONE_RUDA)
        await callback.message.answer(
            "📱 У вас уже указан номер телефона. Хотите заменить его?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да", callback_data="ruda_phone_yes"), InlineKeyboardButton(text="❌ Нет", callback_data="ruda_phone_no")],
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

@router.message(UserState.AWAITING_CONTACT_INFO_RUDA)
async def handle_ruda_contact(message: Message, state: FSMContext, db: Database, bot: Bot):
    info = message.text.strip()
    db.add_user_action(message.from_user.id, "Запись на демо (руда)", info=info)

    await state.set_state(UserState.MAIN_MENU)
    await message.answer("✅ Спасибо! Мы с вами свяжемся в течение 24 часов.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer("Какое направление вас интересует?", reply_markup=InlineKeyboards.direction_selection())

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
    await handle_project_details(callback, ["ugol"], "ugol")

@router.callback_query(F.data == "ugol_demo")
async def ugol_demo(callback: CallbackQuery, state: FSMContext, db: Database):
    if db.has_phone(callback.from_user.id):
        await state.set_state(UserState.CONFIRM_PHONE_UGOL)
        await callback.message.answer(
            "📱 У вас уже указан номер телефона. Хотите заменить его?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да", callback_data="ugol_phone_yes"), InlineKeyboardButton(text="❌ Нет", callback_data="ugol_phone_no")],
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
        "Пожалуйста, напишите контакную информацию <b>одним сообщением</b>\n",
        reply_markup=InlineKeyboards.cancel()
    )
    await callback.answer()

@router.message(UserState.AWAITING_PHONE_UGOL)
async def handle_ugol_phone(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, phone=message.text.strip())
    await state.set_state(UserState.AWAITING_CONTACT_INFO_UGOL)
    await message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\n"
        "Пожалуйста, напишите контакную информацию <b>одним сообщением</b>\n",
        reply_markup=InlineKeyboards.cancel()
    )

@router.message(UserState.AWAITING_CONTACT_INFO_UGOL)
async def handle_ugol_contact(message: Message, state: FSMContext, db: Database, bot: Bot):
    info = message.text.strip()
    db.add_user_action(message.from_user.id, "Запись на демо (уголь)", info=info)

    await state.set_state(UserState.MAIN_MENU)
    await message.answer("✅ Спасибо! Мы с вами свяжемся в течение 24 часов.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS)
    await message.answer("Какое направление вас интересует?", reply_markup=InlineKeyboards.direction_selection())
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
    await handle_project_details(callback, ["ruda", "ugol"], "both")

@router.callback_query(F.data == "both_demo")
async def both_demo(callback: CallbackQuery, state: FSMContext, db: Database):
    if db.has_phone(callback.from_user.id):
        await state.set_state(UserState.CONFIRM_PHONE_BOTH)
        await callback.message.answer(
            "📱 У вас уже указан номер телефона. Хотите заменить его?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да", callback_data="both_phone_yes"), InlineKeyboardButton(text="❌ Нет", callback_data="both_phone_no")],
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
    db.add_user_action(message.from_user.id, "Запись на демо (руда и уголь)", info=info)

    await state.set_state(UserState.MAIN_MENU)
    await message.answer("✅ Спасибо! Мы с вами свяжемся в течение 24 часов.")
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer("Какое направление вас интересует?", reply_markup=InlineKeyboards.direction_selection())

    await notify_manager_about_demo(bot, db, message, "Уголь и Руда")