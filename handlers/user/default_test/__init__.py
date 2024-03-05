from aiogram import Router
from middlewares.throttling import ThrottlingMiddleware

from . import creation_test
from . import test_menu
from . import process_test

default_test_router = Router()
default_test_router.callback_query.middleware(ThrottlingMiddleware())

default_test_router.include_routers(
    creation_test.router,
    test_menu.router,
    process_test.router
)