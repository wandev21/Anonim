from aiogram import Router, Bot, F, types
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION

from database import crud


router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    )
)
async def new_group_handler(event: types.ChatMemberUpdated, bot: Bot):
    is_created, group = await crud.create_group(
        event.chat.id,
        event.chat.title,
        event.chat.username
    )

    await bot.send_message(
        event.chat.id,
        'Привет!'
    )
