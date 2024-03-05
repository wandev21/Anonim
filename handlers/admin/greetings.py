from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from database import crud
from keyboards.admin.greetings import greetings_menu
from keyboards.admin.admin import cancel_action, back_to_menu
from states.admin import GreetingsSG


router = Router()
router.message.filter(F.chat.type == 'private')


@router.callback_query(F.data == 'greetings')
async def create_greeting(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    greeting_exists = await crud.greeting_exists()
    await call.message.edit_text(
        "👋 <b>Настройка приветствия</b>",
        reply_markup=greetings_menu(greeting_exists)
    )


@router.callback_query(F.data == 'change_greeting')
async def change_greeting(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        'Отправь новое приветствие.',
        reply_markup=cancel_action('greetings')
    )
    await state.set_state(GreetingsSG.get_new_greeting)


@router.message(GreetingsSG.get_new_greeting, F.text)
async def get_greeting_post(message: types.Message, state: FSMContext):
    await state.clear()

    await crud.create_greeting(
        message.html_text,
        markup=message.reply_markup.model_dump() if message.reply_markup else []
    )

    await message.answer(
        '<b>Новое приветствие успешно установлено!</b>',
        reply_markup=back_to_menu(with_cancel=False)
    )


@router.callback_query(F.data == 'del_greeting')
async def delete_greeting(call: types.CallbackQuery):
    await crud.delete_greeting()
    await call.answer('Приветствие успешно удалено.')
    await call.message.edit_reply_markup(
        reply_markup=greetings_menu(False)
    )


@router.callback_query(F.data == 'reveal_greeting')
async def delete_greeting(call: types.CallbackQuery):
    greeting = await crud.get_greeting()
    await call.message.answer(greeting.text, reply_markup=greeting.markup if greeting.markup else None)
