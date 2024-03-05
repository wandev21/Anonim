from aiogram import Router

from . import rate_test


rating_router = Router()
rating_router.include_routers(
    rate_test.router
)
