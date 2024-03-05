from aiogram import Router, F

from config import ADMINS

from . import populate_tests
from . import admin_handlers
from . import greetings
from . import delete_test


admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(ADMINS))
admin_router.callback_query.filter(F.from_user.id.in_(ADMINS))

admin_router.include_routers(
    populate_tests.router,
    delete_test.router,
    greetings.router,
    admin_handlers.router,
)
