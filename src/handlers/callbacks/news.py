import json

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext

from pathlib import Path
from config import load_config
from src.states.states import UserState
from src.news.news_manager import NewsManager
from src.keyboards.inline import InlineKeyboards

router = Router()
config = load_config()
news_manager = NewsManager()

BASE_DIR = Path(__file__).parent.parent.parent / "news"
NEWS_DIR = BASE_DIR / "jsonNews"
IMAGES_DIR = BASE_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@router.callback_query(F.data == "news")
async def news_start(callback: CallbackQuery, state: FSMContext):
    """Переход в раздел новостей, открываем первую новость."""
    await state.set_state(UserState.NEWS)
    await send_news(callback, 0)

async def send_news(callback: CallbackQuery, index: int):
    """Отправляет новость по индексу."""
    news_data = news_manager.get_news(index)
    if not news_data:
        await callback.message.answer("❌ Новостей пока нет.")
        return

    text = f"📰 <b>{news_data['title']}</b>\n\n{news_data['text']}"
    keyboard = InlineKeyboards.news_navigation(index, news_manager.total_news, callback.from_user.id)

    if "image" in news_data and news_data["image"]:
        image_path = news_manager.IMAGES_DIR / news_data["image"]
        if image_path.exists():
            file = FSInputFile(str(image_path))
            await callback.message.answer_photo(file, caption=text, reply_markup=keyboard)
        else:
            await callback.message.answer(text, reply_markup=keyboard)
    else:
        await callback.message.answer(text, reply_markup=keyboard)

    await callback.answer()

@router.callback_query(F.data.startswith("news_"))
async def news_navigation(callback: CallbackQuery):
    """Обрабатывает кнопки 'Следующая новость' и 'Предыдущая новость'."""
    index = int(callback.data.split("_")[1])
    await send_news(callback, index)

@router.callback_query(F.data == "add_news")
async def add_news(callback: CallbackQuery, state: FSMContext):
    """Запускает процесс добавления новости (только для админов)."""
    if callback.from_user.id not in config.tg_bot.admins:
        await callback.message.answer("❌ У вас нет прав для добавления новостей.")
        await callback.answer()
        return

    await state.set_state(UserState.WAITING_TITLE)
    await callback.message.answer("📝 Введите заголовок новости:", reply_markup=InlineKeyboards.back_to_main())
    await callback.answer()

@router.message(UserState.WAITING_TITLE)
async def receive_title(message: Message, state: FSMContext):
    """Получает заголовок новости."""
    await state.update_data(title=message.text)
    await state.set_state(UserState.WAITING_DESCRIPTION)
    await message.answer("📄 Теперь введите описание новости:", reply_markup=InlineKeyboards.back_to_main())

@router.message(UserState.WAITING_DESCRIPTION)
async def receive_description(message: Message, state: FSMContext):
    """Получает описание новости."""
    await state.update_data(description=message.text)
    await state.set_state(UserState.WAITING_IMAGE_DECISION)

    await message.answer("📷 Будете загружать фотографию?\n\nВыберите вариант:",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                             [InlineKeyboardButton(text="✅ Да", callback_data="upload_image")],
                             [InlineKeyboardButton(text="❌ Нет", callback_data="save_news")]
                         ]))

@router.callback_query(F.data == "upload_image")
async def request_image(callback: CallbackQuery, state: FSMContext):
    """Запрашивает у пользователя изображение."""
    await state.set_state(UserState.WAITING_IMAGE)
    await callback.message.answer("📷 Отправьте изображение для новости:", reply_markup=InlineKeyboards.back_to_main())
    await callback.answer()

@router.message(UserState.WAITING_IMAGE, F.photo)
async def receive_image(message: Message, state: FSMContext):
    """Сохраняет изображение и завершает процесс добавления новости."""
    data = await state.get_data()
    title, description = data["title"], data["description"]

    news_id = len(list(NEWS_DIR.glob("*.json"))) + 1

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    image_path = IMAGES_DIR / f"{news_id}.jpg"

    await message.bot.download_file(file.file_path, destination=image_path)

    news_data = {"title": title, "text": description, "image": image_path.name}
    with open(NEWS_DIR / f"{news_id}.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=4)

    await state.clear()
    await message.answer("✅ Новость успешно добавлена!", reply_markup=InlineKeyboards.main_menu(message.from_user.id))

@router.callback_query(F.data == "save_news")
async def save_news_without_image(callback: CallbackQuery, state: FSMContext):
    """Сохраняет новость без изображения."""
    data = await state.get_data()
    title, description = data["title"], data["description"]

    news_id = len(list(NEWS_DIR.glob("*.json"))) + 1

    news_data = {"title": title, "text": description}
    with open(NEWS_DIR / f"{news_id}.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=4)

    await state.clear()
    await callback.message.answer("✅ Новость успешно добавлена!", reply_markup=InlineKeyboards.main_menu(callback.from_user.id))
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def cancel_news_creation(callback: CallbackQuery, state: FSMContext):
    """Отмена добавления новости и возврат в главное меню."""
    await state.clear()
    await callback.message.answer("Выберите действие:", reply_markup=InlineKeyboards.main_menu(callback.from_user.id))
    await callback.answer()