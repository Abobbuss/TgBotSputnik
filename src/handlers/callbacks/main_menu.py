from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from src.states.states import UserState
from src.keyboards.inline import InlineKeyboards
from src.utils.presentation_manager import PresentationManager

router = Router()

@router.callback_query(F.data == "projects")
async def projects_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.PROJECTS)
    await callback.message.answer("Вы в разделе 'Наши проекты'. Выберите опцию:", reply_markup=InlineKeyboards.projects_menu())

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.MAIN_MENU)
    await callback.message.answer("Выберите действие:", reply_markup=InlineKeyboards.main_menu(callback.from_user.id))

@router.callback_query(F.data == "presentation")
async def send_latest_presentation(callback: CallbackQuery):
    """Отправляет последнюю загруженную презентацию."""
    latest_presentation = PresentationManager.get_latest_presentation()

    if latest_presentation:
        file = FSInputFile(str(latest_presentation))
        await callback.message.answer_document(file, caption="📄 Вот последняя презентация.")
    else:
        await callback.message.answer("❌ Последняя презентация не найдена.")

    await callback.message.answer("Выберите действие:", reply_markup=InlineKeyboards.main_menu(callback.from_user.id))
    await callback.answer()
