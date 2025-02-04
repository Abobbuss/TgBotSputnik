from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.states.states import UserState
from src.keyboards.inline import InlineKeyboards

router = Router()

@router.callback_query(F.data == "projects")
async def projects_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.PROJECTS)
    await callback.message.answer("Вы в разделе 'Наши проекты'. Выберите опцию:", reply_markup=InlineKeyboards.projects_menu())

@router.callback_query(F.data == "news")
async def news_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.NEWS)
    await callback.message.answer("Вы в разделе 'Новости спутника'. Выберите опцию:", reply_markup=InlineKeyboards.news_menu())

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.MAIN_MENU)
    await callback.message.answer("Выберите действие:", reply_markup=InlineKeyboards.main_menu())
