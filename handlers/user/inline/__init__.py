from aiogram import Router

from . import get_test
from . import tests
from . import chosen_result


inline_router = Router()
inline_router.include_routers(
    get_test.router,
    tests.router,
    chosen_result.router
)
