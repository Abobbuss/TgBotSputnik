from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.states.states import UserState
from src.keyboards.inline import InlineKeyboards
from src.constants import message_constants

router = Router()

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.set_state(UserState.MAIN_MENU)
    await message.answer(message_constants.welcome_message + "\nВыберите действие:", reply_markup=InlineKeyboards.main_menu())
