import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from keyboards import all_routers as handlers_routers
from services import all_routers as services_routers


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    for router in handlers_routers + services_routers:
        dp.include_router(router)

    await dp.start_polling(bot)


asyncio.run(main())



