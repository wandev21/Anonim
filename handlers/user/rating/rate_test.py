from aiogram import Router, F, Bot, types

from database import crud
from keyboards.tests.for_rating import RateTestCF


router = Router()


@router.callback_query(RateTestCF.filter())
async def handle(call: types.CallbackQuery, callback_data: RateTestCF):
    await crud.rate_or_update(call.from_user.id, callback_data.test_id, callback_data.value)
    await call.answer(f'Вы успешно оценили тест на ⭐{callback_data.value}', show_alert=True)
    try:
        await call.message.delete()
    except:
        pass
