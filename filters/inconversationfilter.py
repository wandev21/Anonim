from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message

from database import crud

class InConversationFilter(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        user = await crud.get_anonim(
            user_id=message.from_user.id
        )

        if not user: return False

        if user.status != 'default':
            return True
        else:
            return False