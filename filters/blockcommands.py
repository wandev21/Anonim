from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message

from database import crud

from utils.texts import ANONCHAT_BLOCK_COMMAND

class BlockCommandInConversaton(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        user = await crud.get_anonim(
            user_id=message.from_user.id
        )

        try:
            if user.status == 'default':
                return True
            else:
                await message.answer(ANONCHAT_BLOCK_COMMAND)
                return False
        except:
            return True