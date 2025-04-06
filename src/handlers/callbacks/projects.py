from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.keyboards.inline import InlineKeyboards
from src.projects.projects import RudaProject, UgolProject
from src.states.states import UserState

router = Router()

ruda = RudaProject()
ugol = UgolProject()


@router.callback_query(F.data == "choose_ruda")
async def choose_ruda(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SHOW_RUDA_OPTIONS)
    await callback.message.answer("Вы выбрали направление Руды. Что вас интересует?", reply_markup=InlineKeyboards.project_options_keyboard("ruda"))
    await callback.answer()


@router.callback_query(F.data == "choose_ugol")
async def choose_ugol(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SHOW_UGOL_OPTIONS)
    await callback.message.answer("Вы выбрали направление Уголь. Что вас интересует?", reply_markup=InlineKeyboards.project_options_keyboard("ugol"))
    await callback.answer()


@router.callback_query(F.data == "choose_both")
async def choose_both(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.SHOW_BOTH_OPTIONS)

    await callback.message.answer(
        "<b>Руда и уголь.</b>\nЧто вас интересует?",
        reply_markup=InlineKeyboards.project_options_keyboard("ugol")
    )

    await callback.answer()
