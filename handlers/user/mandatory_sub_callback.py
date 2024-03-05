from aiogram import Router, Bot, F, types

from tortoise.expressions import F as tF

from database import crud
from database.models import Users, Subs

from utils.admin import check_follow
from utils.texts import SUB_TEXT
from keyboards.mandatory_subscription import unsubbed


router = Router()


@router.callback_query(F.data == 'continue')
async def subscription_done(call: types.CallbackQuery, bot: Bot):
    user = await crud.get_user(call.from_user.id)
    follows = await check_follow(user, bot)

    if follows and "subs" in follows:
        return await call.message.answer(
            SUB_TEXT,
            reply_markup=unsubbed(follows)
        )

    await call.message.delete()
    await call.message.answer(
        "<b>Вы успешно подписались на все каналы!</b> Нажмите /start для продолжения."
    )
    await crud.update_sub_counter(user.id)
