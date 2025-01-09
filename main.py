import asyncio
import logging
import config
from database import create_table
from aiogram import Bot, Dispatcher
from routers import router as main_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)

dp = Dispatcher()

dp.include_router(main_router)


# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())