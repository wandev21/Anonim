from aiogram import Router, types,  F, Bot
from aiogram.fsm.context import FSMContext

from database import crud

from keyboards import default_test

from utils import texts

router = Router()

@router.message(F.text == '📋 Тесты')
async def anonim_test(message: types.Message):
    user_id=message.from_user.id
    await message.answer(
        texts.DEFAULT_TEST_MENU
    )
    count = await crud.get_default_test_quantity(
        user_id=user_id
    )
    await message.answer(
        text=f'Список твоих тестов ({len(count)})',
        reply_markup=default_test.default_test_menu(user_id=user_id,tests=count)
    )

@router.callback_query(F.data == 'patterns')
@router.callback_query(F.data == 'back_to_patterns')
async def patterns_menu(call: types.CallbackQuery):
    await call.message.edit_text(
        text='Список шаблонов для тестов:',
        reply_markup=default_test.tests_petterns()
    )

@router.callback_query(F.data.startswith('deftest'))
async def patterns(call: types.CallbackQuery):
    test_type = call.data.split('_')[1]

    await call.message.edit_text(
        text=texts.PATTERNS_TEXT[test_type],
        reply_markup=default_test.pattern(test_type=test_type)
    )

@router.callback_query(F.data.startswith('show'))
async def show_test(call: types.CallbackQuery):
    test_type=call.data.split('_')[1]
    await call.message.answer(
        text=f'💬 Тест "{texts.DEFAULT_TESTS_NAMES[test_type]}"\n\n'
        '😋 Хочешь изменить его?',
        reply_markup=default_test.showing_test(
            user_id=call.from_user.id,
            test_type=test_type
        )
    )

@router.callback_query(F.data.startswith('getlink'))
async def get_link(call: types.CallbackQuery, bot: Bot):
    test_type=call.data.split('_')[1]
    me = await bot.me()
    await call.message.edit_text(
        text=f'💬 Тест "{texts.DEFAULT_TESTS_NAMES[test_type]}"\n\n'
        '👇 Ссылка на тест:\n'
        f't.me/{me.username}?start=dt_{test_type}_{call.from_user.id}'
    )
