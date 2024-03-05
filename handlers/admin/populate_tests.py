from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import crud
from keyboards.user_menu import user_menu
from utils.tests_parser import parse_file
from states.admin import PopulateTestsSG


router = Router()


@router.message(Command("populate_tests"))
async def populate_tests_cmd(message: types.Message, state: FSMContext):
    await state.set_state(PopulateTestsSG.get_file)
    await message.answer('Пришлите мне файл с тестами.', reply_markup=types.ReplyKeyboardRemove())


@router.message(F.document, PopulateTestsSG.get_file)
async def get_file_with_tests(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    msg = await message.answer(
        'Начинаю процесс вставки новых тестов. Вам придет сообщение по окончании.',
        reply_markup=user_menu()
    )

    file = await bot.get_file(message.document.file_id)
    await bot.download_file(file.file_path, 'tests.txt')

    tests_data = parse_file('tests.txt')
    success_tests, success_answers, error_tests = await crud.add_tests_and_answers_from_parser(tests_data)

    await message.answer(
        f'<b>Готово!</b>\n\n'
        f'<b>Добавленных тестов: {success_tests}</b>\n'
        f'<b>Добавленных ответов: {success_answers}</b>\n'
        f'<b>Не удалось добавить: {error_tests} тестов.</b>',
        reply_to_message_id=msg.message_id
    )
