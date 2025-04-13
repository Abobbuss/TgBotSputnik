from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext

from pathlib import Path

from src.constants import message_constants
from src.models.db import Database
from src.states.states import UserState
from src.keyboards.inline import InlineKeyboards

router = Router()


@router.callback_query(F.data == "get_materials")
async def send_round_table_materials(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.GET_DATA_ROUND_TABLE)

    materials_dir = Path(__file__).parent.parent.parent / "files" / "roundTable"

    if not materials_dir.exists() or not materials_dir.is_dir():
        await callback.message.answer("❌ Пока что нет доступных материалов.")
        await callback.answer()
        return

    files = list(materials_dir.glob("*.*"))

    if not files:
        await callback.message.answer("❌ Пока что нет доступных материалов.")
        await callback.answer()
        return

    await callback.message.answer("📦 Загружаем материалы круглого стола...")

    for file_path in files:
        try:
            file = FSInputFile(file_path)
            await callback.message.answer_document(file)
        except Exception as e:
            await callback.message.answer(f"⚠️ Не удалось отправить файл, попробуйте позже.")

    await callback.message.answer("📦 Хотите получить запись круглого стола?", reply_markup= InlineKeyboards.get_video_round_table())


@router.callback_query(F.data == "get_video_to_round_table")
async def send_round_table_video(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_EMAIL_ROUND_TABLE)
    await callback.message.answer("✉️ Введите свой email для получения записи круглого стола:", reply_markup= InlineKeyboards.cancel())
    await callback.answer()


@router.message(UserState.AWAITING_EMAIL_ROUND_TABLE)
async def handle_round_table_email(message: Message, state: FSMContext, db: Database):
    email = message.text.strip()

    db.add_user_action(message.from_user.id, "Запрос видео круглого стола", info=email)

    await message.answer("✅ Спасибо! Мы отправим на указанный email запись круглого столка, как только она появится.")
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer(message_constants.SOCIAL_TEXT)
    await message.answer("<b>Главное меню</b>, выберите действие:", reply_markup=InlineKeyboards.start_menu(message.from_user.id))
    await state.clear()


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.MAIN_MENU)
    await callback.message.edit_text(
        "📋 <b>Главное меню</b>, выберите действие:",
        reply_markup=InlineKeyboards.start_menu(callback.from_user.id)
    )
    await callback.answer()


@router.callback_query(F.data == "select_direction")
async def select_work_direction(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SELECT_DIRECTION)
    await callback.message.answer(
        "🔍 В каком направлении вы работаете?",
        reply_markup=InlineKeyboards.direction_selection()
    )
    await callback.answer()
