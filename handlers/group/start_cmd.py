from aiogram import Router, Bot, types, html
from aiogram.filters import Command

from database import crud
from utils import texts


router = Router()


@router.message(Command('start'))
async def start_cmd(message: types.Message, bot: Bot):
    source = message.text.split(' ')[1] if ' ' in message.text else None
    group, is_created = await crud.create_group(
        message.chat.id,
        html.quote(message.chat.title),
        message.chat.username,
        source
    )

    # me = await bot.me()
    # await message.answer(
    #     texts.CHAT_JOIN_TEXT,
    # )
