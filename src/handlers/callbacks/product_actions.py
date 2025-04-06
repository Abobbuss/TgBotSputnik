from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from src.constants import message_constants
from src.states.states import UserState
from src.models.db import Database

router = Router()


# === RUDA ===

@router.callback_query(F.data == "ruda_details")
async def ruda_details(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_EMAIL_RUDA)
    await callback.message.answer("📧 Напишите свой email: мы пришлем вам запись выступлений Круглого стола.")
    await callback.answer()


@router.callback_query(F.data == "ruda_demo")
async def ruda_demo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_CONTACT_INFO_RUDA)
    await callback.message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\n"
        "Можете написать в одной строке или через запятую."
    )
    await callback.answer()


@router.message(UserState.AWAITING_EMAIL_RUDA)
async def handle_ruda_email(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, email=message.text)
    db.add_user_action(message.from_user.id, "Запрос записи круглого стола (руда)")

    await message.answer("✅ Спасибо! Видео будет отправлено на указанную почту.")
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer(message_constants.SOCIAL_TEXT)
    await state.clear()


@router.message(UserState.AWAITING_CONTACT_INFO_RUDA)
async def handle_ruda_contact(message: Message, state: FSMContext, db: Database):
    parts = [p.strip() for p in message.text.split(",")]

    db.update_user_info(
        message.from_user.id,
        name=parts[0] if len(parts) > 0 else None,
        email=parts[1] if len(parts) > 1 else None,
        company=parts[2] if len(parts) > 2 else None,
        position=parts[3] if len(parts) > 3 else None
    )
    db.add_user_action(message.from_user.id, "Запись на демо (руда)")

    await state.set_state(UserState.AWAITING_SHARE_AFTER_CONTACT_RUDA)
    await message.answer("✅ Спасибо! Теперь вы можете поделиться Telegram-аккаунтом.",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="📩 Поделиться Telegram-аккаунтом", callback_data="ruda_share")]
                         ]))


@router.callback_query(F.data == "ruda_share")
async def handle_ruda_share(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await callback.message.answer(message_constants.SOCIAL_TEXT)
    await state.clear()
    await callback.answer()


# === UGOL ===

@router.callback_query(F.data == "ugol_details")
async def ugol_details(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_EMAIL_UGOL)
    await callback.message.answer("📧 Напишите свой email: мы пришлем вам запись выступлений Круглого стола.")
    await callback.answer()


@router.callback_query(F.data == "ugol_demo")
async def ugol_demo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.AWAITING_CONTACT_INFO_UGOL)
    await callback.message.answer(
        "📄 Укажите ваше имя, email, компанию и должность.\n\n"
        "Можете написать в одной строке или через запятую.\n"
        "Мы свяжемся с вами в течение 24 часов для уточнения деталей."
    )
    await callback.answer()


@router.message(UserState.AWAITING_EMAIL_UGOL)
async def handle_ugol_email(message: Message, state: FSMContext, db: Database):
    db.update_user_info(message.from_user.id, email=message.text)
    db.add_user_action(message.from_user.id, "Запрос записи круглого стола (уголь)")

    await message.answer("✅ Спасибо! Видео будет отправлено на указанную почту.")
    await message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await message.answer(message_constants.SOCIAL_TEXT)
    await state.clear()


@router.message(UserState.AWAITING_CONTACT_INFO_UGOL)
async def handle_ugol_contact(message: Message, state: FSMContext, db: Database):
    parts = [p.strip() for p in message.text.split(",")]

    db.update_user_info(
        message.from_user.id,
        name=parts[0] if len(parts) > 0 else None,
        email=parts[1] if len(parts) > 1 else None,
        company=parts[2] if len(parts) > 2 else None,
        position=parts[3] if len(parts) > 3 else None
    )
    db.add_user_action(message.from_user.id, "Запись на демо (уголь)")

    await state.set_state(UserState.AWAITING_SHARE_AFTER_CONTACT_UGOL)
    await message.answer("✅ Спасибо! Теперь вы можете поделиться Telegram-аккаунтом.",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="📩 Поделиться Telegram-аккаунтом", callback_data="ugol_share")]
                         ]))


@router.callback_query(F.data == "ugol_share")
async def handle_ugol_share(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(message_constants.SOCIAL_LINKS, disable_web_page_preview=True)
    await callback.message.answer(message_constants.SOCIAL_TEXT)
    await state.clear()
    await callback.answer()
