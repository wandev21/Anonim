from aiogram import Router, F, Bot, types

from database import crud
from keyboards.user_menu import RANDOM_TEST_TEXT
from keyboards.tests.for_test_pass import group_result_menu
from utils.telegram import get_text_for_test


router = Router()


@router.message(F.text == RANDOM_TEST_TEXT)
async def handle(message: types.Message, bot: Bot):
    test = await crud.get_random_test()
    if test is None:
        return await message.answer('Тестов пока нет.')

    message_text = get_text_for_test(test, True)
    await message.answer(message_text, reply_markup=group_result_menu(test.id, (await bot.me()).username))
    await crud.increment_pass_counter(int(test.id))
