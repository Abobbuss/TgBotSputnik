from aiogram import Router, F
from aiogram.types import CallbackQuery
from config import load_config
from src.keyboards.inline import InlineKeyboards

router = Router()
config = load_config()

@router.callback_query(F.data == "upload_presentation")
async def request_presentation(callback: CallbackQuery):
    """Отправляет запрос на загрузку презентации (только для админов)."""
    if callback.from_user.id not in config.tg_bot.admins:
        await callback.message.answer("❌ У вас нет прав для загрузки презентаций.")
        await callback.answer()
        return

    await callback.message.answer("📤 Скиньте новую презентацию (формат: .pptx)", reply_markup=InlineKeyboards.back_to_main())
    await callback.answer()
