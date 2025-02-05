from aiogram import Router, F
from aiogram.types import Message
from pathlib import Path
from config import load_config
from src.keyboards.inline import InlineKeyboards

router = Router()
config = load_config()

PRESENTATION_DIR = Path(__file__).parent.parent.parent / "latest_presentations"
PRESENTATION_DIR.mkdir(exist_ok=True)

@router.message(F.document)
async def save_presentation(message: Message):
    """Сохраняет загруженную презентацию (только админы)."""
    if message.from_user.id not in config.tg_bot.admins:
        await message.answer("❌ У вас нет прав для загрузки презентаций.")
        return

    document = message.document
    if not document.file_name.endswith(".pptx"):
        await message.answer("❌ Загружайте только файлы .pptx")
        return

    file_path = PRESENTATION_DIR / document.file_name
    await message.bot.download(document, destination=file_path)

    await message.answer("✅ Презентация загружена!", reply_markup=InlineKeyboards.main_menu(message.from_user.id))
