from aiogram import Router, Bot, types
from aiogram.filters.command import Command, CommandObject

from database import crud
from keyboards.tests.for_test_pass import group_result_menu
from keyboards.admin.delete_test import DeleteTestCD, delete_test_menu
from utils.telegram import get_text_for_test


router = Router()


@router.message(Command('del_test'))
async def show_test_by_id(message: types.Message, bot: Bot, command: CommandObject):
    test = await crud.get_test_by_id(int(command.args), prefetch_answers=True)
    if test is None:
        return await message.answer('Такого теста не существует.')

    message_text = get_text_for_test(test, True)
    await message.answer(message_text, reply_markup=delete_test_menu(test.id))


@router.callback_query(DeleteTestCD.filter())
async def delete_test(call: types.CallbackQuery, callback_data: DeleteTestCD):
    test_id = callback_data.test_id
    await crud.delete_test_by_id(test_id)

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.reply('Тест успешно удалён.')
