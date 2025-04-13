from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.constants import message_constants
from src.keyboards.inline import InlineKeyboards
from src.projects.projects import RudaProject, UgolProject
from src.states.states import UserState

router = Router()

ruda = RudaProject()
ugol = UgolProject()


@router.callback_query(F.data == "choose_ruda")
async def choose_ruda(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SHOW_RUDA_OPTIONS)
    await callback.message.answer(message_constants.GEOS_RUDA_TEXT, reply_markup=InlineKeyboards.project_options_keyboard("ruda"))
    await callback.answer()


@router.callback_query(F.data == "choose_ugol")
async def choose_ugol(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SHOW_UGOL_OPTIONS)
    await callback.message.answer(message_constants.GEOS_UGOL_TEXT, reply_markup=InlineKeyboards.project_options_keyboard("ugol"))
    await callback.answer()


@router.callback_query(F.data == "choose_both")
async def choose_both(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SHOW_BOTH_OPTIONS)

    combined_text = (
        f"{message_constants.GEOS_RUDA_TEXT}\n\n"
        f"{message_constants.GEOS_UGOL_TEXT}"
    )

    await callback.message.answer(
        combined_text,
        reply_markup=InlineKeyboards.project_options_keyboard("both")
    )

    await callback.answer()
