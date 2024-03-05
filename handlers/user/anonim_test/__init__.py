from aiogram import Router
from middlewares.throttling import ThrottlingMiddleware

from . import get_link
from . import process_test

anonim_test_router = Router()
anonim_test_router.callback_query.middleware(ThrottlingMiddleware())

anonim_test_router.include_routers(
    get_link.router,
    process_test.router
)