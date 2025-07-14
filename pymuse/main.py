from config import config

import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers import main_router, commands
from migrate import migrate

migrate()

logging.basicConfig(level=logging.INFO, force=True)


async def main():
    bot = Bot(config.token)
    await bot.set_my_commands(commands)
    dp = Dispatcher()
    dp.include_router(main_router)
    print("bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot stoppend")
