from aiogram import Router, F, Bot, types
from aiogram.filters import Command

from database import crud
from keyboards.user_menu import TOP_TEXT
from keyboards.tests.for_top_tests import top_menu
from keyboards.mandatory_subscription import unsubbed
from utils import texts
from utils.admin import show_ad_pm, check_follow


router = Router()


@router.message(F.text == TOP_TEXT)
async def handle_command(message: types.Message, bot: Bot):
    user = await crud.get_user(message.from_user.id)
    follows = await check_follow(user, bot)
    if follows and "subs" in follows:
        return await message.answer(
            texts.SUB_TEXT,
            reply_markup=unsubbed(follows)
        )

    await message.answer(
        texts.TOP_DESC,
        reply_markup=top_menu()
    )

    await show_ad_pm(message.from_user.id, bot)
