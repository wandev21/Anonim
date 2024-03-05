from aiogram import Router
from middlewares.throttling import ThrottlingMiddleware

from . import anonchat_main
from . import conversation
from . import profile


anonim_router = Router()

anonim_router.include_routers(
    anonchat_main.router,
    conversation.router,
    profile.router
)