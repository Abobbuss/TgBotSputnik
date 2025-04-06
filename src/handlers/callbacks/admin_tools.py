from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from config import load_config

from src.states.states import UserState
from src.models.db import Database

import qrcode
from io import BytesIO
from pathlib import Path

router = Router()
config = load_config()

BOT_NAME = "Sputnikkk_bot"


@router.callback_query(F.data == "generate_qr")
async def request_referral_name(callback: CallbackQuery, state: FSMContext):
    """Запрашивает имя реферала у администратора"""
    if callback.from_user.id not in config.tg_bot.admins:
        await callback.message.answer("❌ У вас нет доступа к генерации QR.")
        await callback.answer()
        return

    await state.set_state(UserState.AWAITING_REFERRAL_NAME)
    await callback.message.answer("✏️ Введите имя реферала (латиницей, например: ivan)")
    await callback.answer()


@router.message(UserState.AWAITING_REFERRAL_NAME)
async def generate_qr_code(message: Message, state: FSMContext):
    referral_name = message.text.strip().lower().replace(" ", "_")

    if not referral_name.isalnum():
        await message.answer("❌ Имя должно быть латиницей, без пробелов и символов.")
        return

    bot_link = f"https://t.me/{BOT_NAME}?start={referral_name}"

    # Генерация QR
    qr = qrcode.make(bot_link)
    buffer = BytesIO()
    save_dir = Path("qr")
    save_dir.mkdir(parents=True, exist_ok=True)

    # Путь до файла
    file_path = save_dir / f"qr_{referral_name}.png"

    # Сохраняем QR
    qr.save(file_path)
    buffer.seek(0)  # ✅ обязательно передать в начало

    file = FSInputFile(path=file_path)

    await message.answer_document(
        document=file,
        caption=f"✅ QR для <b>{referral_name}</b>\nСсылка: {bot_link}",
    )

    await state.clear()


@router.callback_query(F.data == "show_all_qr")
async def show_all_qr(callback: CallbackQuery):
    if callback.from_user.id not in config.tg_bot.admins:
        await callback.message.answer("❌ Неизвестная команда.")
        await callback.answer()
        return

    qr_dir = Path("qr")
    if not qr_dir.exists():
        await callback.message.answer("❌ Папка с QR-кодами не найдена.")
        await callback.answer()
        return

    qr_files = list(qr_dir.glob("qr_*.png"))

    if not qr_files:
        await callback.message.answer("❌ Нет сохранённых QR-кодов.")
        await callback.answer()
        return

    for qr_file in qr_files:
        # Извлекаем имя: qr_ivan.png → ivan
        referral_name = qr_file.stem.replace("qr_", "")
        file = FSInputFile(path=qr_file)

        await callback.message.answer_document(
            document=file,
            caption=f"📎 QR для <b>{referral_name}</b>",
        )

    await callback.answer()


@router.callback_query(F.data == "show_user_count")
async def show_user_count(callback: CallbackQuery, db: Database):
    count = len(db.get_all_users())
    await callback.message.answer(f"👥 Общее количество пользователей: <b>{count}</b>")
    await callback.answer()


@router.callback_query(F.data == "show_referrals")
async def show_referrals(callback: CallbackQuery, db: Database):
    referrals = db.get_all_referrals()

    if not referrals:
        await callback.message.answer("Пока никто не пришёл по реферальным ссылкам.")
    else:
        text = "<b>📊 Рефералы:</b>\n"
        for name, count in referrals:
            text += f"• {name}: <b>{count}</b>\n"

        await callback.message.answer(text)

    await callback.answer()


@router.callback_query(F.data == "show_user_requests")
async def show_user_requests(callback: CallbackQuery, db: Database):
    actions = db.get_all_user_actions()

    if not actions:
        await callback.message.answer("Нет запросов от пользователей.")
        await callback.answer()
        return

    # Разбиваем на порции, чтобы не превысить лимиты Telegram
    messages = []
    for tg_id, name, email, company, position, action, time in actions:
        msg = (
            f"👤 <b>{name or 'Без имени'}</b> (ID: <code>{tg_id}</code>)\n"
            f"📧 Email: {email or '—'}\n"
            f"🏢 Компания: {company or '—'}\n"
            f"💼 Должность: {position or '—'}\n"
            f"📌 Запрос: <i>{action}</i>\n"
            f"🕓 Время: {time}\n"
            f"{'-'*30}\n"
        )
        messages.append(msg)

    # Отправляем по 5 записей за раз
    for i in range(0, len(messages), 5):
        chunk = "".join(messages[i:i+5])
        await callback.message.answer(chunk)

    await callback.answer()