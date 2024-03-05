from aiogram import Router, F
from middlewares.throttling import ThrottlingMiddleware

from . import catalogue
from . import create_test
from . import my_tests
from . import start_cmd
from . import mandatory_sub_callback
from . import top_tests
from . import random_test


user_router = Router()
user_router.message.filter(F.chat.type == 'private')
user_router.callback_query.filter(F.message.chat.type == 'private')

user_router.include_routers(
    start_cmd.router,
    random_test.router,
    create_test.router,
    my_tests.router,
    catalogue.router,
    top_tests.router,
    mandatory_sub_callback.router
)
