# stdlib
import asyncio
import logging

# thirdparty
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# project
from common.db_settings import Session
from telegram_bot.commands.commands import register_handlers
from telegram_bot.config import tg_settings

# Configure logging
logging.basicConfig(level=logging.INFO)


async def main() -> None:
    """Основная функция для запуска бота"""

    storage = MemoryStorage()
    bot = Bot(token=tg_settings.token)
    bot["db"] = Session
    dp = Dispatcher(bot, storage=storage)
    register_handlers(dp)

    try:
        await dp.start_polling()
    except (KeyboardInterrupt, SystemExit):
        logging.error("Остановка бота...")
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await dp.stop_polling()


if __name__ == "__main__":
    asyncio.run(main())
