from aiogram import Router, F, Bot, types
from aiogram.filters import Command

from database import crud
from keyboards.user_menu import CATALOGUE_TEXT
from keyboards.tests.for_catalogue import catalogue_menu
from keyboards.mandatory_subscription import unsubbed
from utils import texts
from utils.admin import show_ad_pm, check_follow


router = Router()


@router.message(Command('test'))
@router.message(F.text == CATALOGUE_TEXT)
async def handle_command(message: types.Message, bot: Bot):
    user = await crud.get_user(message.from_user.id)
    follows = await check_follow(user, bot)
    if follows and "subs" in follows:
        return await message.answer(
            texts.SUB_TEXT,
            reply_markup=unsubbed(follows)
        )

    categories = await crud.get_all_categories()
    await message.answer(
        texts.CATALOGUE_DESC,
        reply_markup=catalogue_menu(categories)
    )

    await show_ad_pm(message.from_user.id, bot)
