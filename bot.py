import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers import user_router, admin_router, inline_router, group_router, anonim_router, anonim_test_router, default_test_router


from config import BOT_TOKEN, DB_URL
from database import init_database
from utils.telegram import set_commands


async def main():
    await init_database(DB_URL)

    dp = Dispatcher()
    dp.include_routers(
        user_router,
        group_router,
        admin_router,
        inline_router,
        anonim_test_router,
        anonim_router,
        default_test_router
    )

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    await set_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    asyncio.run(main())
