import asyncio

from aiogram import Dispatcher, Bot

from app.handlers import router
from database.models import init_db
from app.schedules import notify_users
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TOKEN

bot = Bot(token=TOKEN)

dp = Dispatcher()


async def on_startup():
    print('Bot started')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_users, 'interval', args=(bot,), minutes=10)
    scheduler.start()


async def main():
    await init_db()
    dp.include_router(router=router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
