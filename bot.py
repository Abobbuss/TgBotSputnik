import asyncio
import sys
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import ClientTimeout

from config import Config, load_config
from src.logs.logger import Logger
from src.handlers.start import router as start_router
from src.handlers.callbacks.main_menu import router as main_menu_router
from src.handlers.callbacks.projects import router as project_router
from src.handlers.callbacks.product_actions import router as product_actions_router
from src.handlers.callbacks.admin_tools import router as admin_router
from src.models.db import Database

logger = Logger()

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
               "[%(asctime)s] - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    config: Config = load_config()

    bot: Bot = Bot(token=config.tg_bot.token, timeout=ClientTimeout(total=15), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp: Dispatcher = Dispatcher()

    db = Database()
    dp["db"] = db
    dp["bot"] = bot

    dp.include_router(start_router)
    dp.include_router(main_menu_router)
    dp.include_router(project_router)
    dp.include_router(product_actions_router)
    dp.include_router(admin_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)  # Удаляем вебхук и очищаем старые обновления
        await dp.start_polling(bot, skip_updates=True, drop_pending_updates=True)
        logger.info("Starting polling...")
    except Exception as e:
        logging.error("Failed to fetch updates - %s: %s", type(e).__name__, e)
    finally:
        try:
            await dp.start_polling(bot, skip_updates=True, drop_pending_updates=True)
        except asyncio.CancelledError:
            logger.info("Tasks were cancelled.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
