from aiogram import Router, types,  F, Bot
from aiogram.fsm.context import FSMContext

from utils import texts

router = Router()

@router.message(F.text == '📨 Анонимные опросы')
async def anonim_test(message: types.Message, bot: Bot):
    me = await bot.me()
    
    await message.answer(
        texts.ANONTEST_INIT
    )
    await message.answer(
        texts.ANONTEST_LINK.format(
            bot_username=me.username,
            user_id=message.from_user.id
        ),
        disable_web_page_preview=False
    )