from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from pathlib import Path

from src.states.states import UserState
from src.keyboards.inline import InlineKeyboards

router = Router()


@router.callback_query(F.data == "get_materials")
async def send_round_table_materials(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.MAIN_MENU)

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

    await callback.answer()


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
