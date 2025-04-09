import qrcode
import re
import xlsxwriter

from datetime import datetime
from io import BytesIO
from pathlib import Path
from collections import Counter

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from config import load_config

from src.states.states import UserState
from src.models.db import Database

router = Router()
config = load_config()

BOT_NAME = "TheGEOS_bot"


@router.callback_query(F.data == "generate_qr")
async def request_referral_name(callback: CallbackQuery, state: FSMContext):
    """Запрашивает имя реферала у администратора"""
    if callback.from_user.id not in config.tg_bot.admins:
        await callback.message.answer("❌ Неизвестная команда.")
        await callback.answer()
        return

    await state.set_state(UserState.AWAITING_REFERRAL_NAME)
    await callback.message.answer("✏️ Введите имя реферала (латиницей, например: ivan)")
    await callback.answer()


@router.message(UserState.AWAITING_REFERRAL_NAME)
async def generate_qr_code(message: Message, state: FSMContext):
    referral_name = message.text.strip().lower().replace(" ", "_")

    if not re.fullmatch(r'[a-z0-9_]+', referral_name):
        await message.answer("❌ Имя должно быть латиницей (a-z), без пробелов и символов, кроме подчёркивания.")
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
        referral_name = qr_file.stem.replace("qr_", "")
        bot_link = f"https://t.me/{BOT_NAME}?start={referral_name}"  # ← добавили ссылку
        file = FSInputFile(path=qr_file)

        await callback.message.answer_document(
            document=file,
            caption=f"📎 QR для <b>{referral_name}</b>\nСсылка: {bot_link}",
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
        await callback.answer()
        return

    text = "<b>📊 Статистика по рефералам:</b>\n"

    for ref_name, count in referrals:
        users = db.get_users_by_ref(ref_name)
        user_ids = [u[0] for u in users]  # telegram_id
        actions_counter = Counter()

        for user_id in user_ids:
            actions = db.get_user_actions_by_telegram_id(user_id)
            for action in actions:
                actions_counter[action] += 1

        text += f"\n<b>👤 {ref_name}</b>: всего пользователей — <b>{count}</b>\n"
        if actions_counter:
            for action_name, action_count in actions_counter.items():
                text += f"  • {action_name}: <b>{action_count}</b>\n"
        else:
            text += "  • Нет активности\n"

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "show_user_requests")
async def show_user_requests(callback: CallbackQuery, db: Database):
    actions = db.get_all_user_actions()

    if not actions:
        await callback.message.answer("Нет запросов от пользователей.")
        await callback.answer()
        return

    # Создаём папку для отчётов
    save_dir = Path("reports")
    save_dir.mkdir(parents=True, exist_ok=True)

    filename = f"user_requests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = save_dir / filename

    # Создаём Excel-файл
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet("User Requests")

    # Заголовки
    headers = ["Telegram ID", "Username", "Инфо", "Телефон", "Запрос", "Время"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Данные
    for row_num, (tg_id, username, info, phone, action, time) in enumerate(actions, start=1):
        worksheet.write(row_num, 0, tg_id)
        worksheet.write(row_num, 1, username or "—")
        worksheet.write(row_num, 2, info or "—")
        worksheet.write(row_num, 3, phone or "—")
        worksheet.write(row_num, 4, action)
        worksheet.write(row_num, 5, time)

    workbook.close()

    # Отправляем Excel-файл
    file = FSInputFile(path=file_path)
    await callback.message.answer_document(
        document=file,
        caption="📊 Все пользовательские запросы:"
    )

    await callback.answer()