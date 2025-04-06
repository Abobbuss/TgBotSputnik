from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from src.states.states import UserState
from src.keyboards.inline import InlineKeyboards

router = Router()


@router.callback_query(F.data == "get_materials")
async def send_round_table_materials(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.MAIN_MENU)
    # Пока не отправляем реальные материалы — просто заглушка
    await callback.message.answer("📄 Материалы круглого стола скоро будут доступны для скачивания.")
    await callback.answer()


@router.callback_query(F.data == "select_direction")
async def select_work_direction(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SELECT_DIRECTION)
    await callback.message.answer(
        "🔍 В каком направлении вы работаете?",
        reply_markup=InlineKeyboards.direction_selection()
    )
    await callback.answer()
