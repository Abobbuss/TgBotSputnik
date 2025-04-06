from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.states.states import UserState
from src.keyboards.inline import InlineKeyboards
from src.constants import message_constants
from src.models.db import Database

router = Router()

@router.message(F.text.regexp(r"^/start(\s+.*)?$"))
async def start(message: Message, state: FSMContext, db: Database):
    args = message.text.split()
    referral = args[1] if len(args) > 1 else None

    db.add_user(message.from_user.id, referral)

    await state.set_state(UserState.MAIN_MENU)
    await message.answer(message_constants.welcome_message + "\nВыберите действие:", reply_markup=InlineKeyboards.start_menu(message.from_user.id))
