from aiogram import Router, types,  F
from aiogram.fsm.context import FSMContext

from database import crud

from keyboards.anonchat import registration
from keyboards.user_menu import anon_menu
from states.user import Registration

from utils import texts

from filters.blockcommands import BlockCommandInConversaton

router = Router()

@router.message(F.text == '✉️ Анонимный чат', BlockCommandInConversaton())
async def anonim_menu(message: types.Message, state: FSMContext):
    await state.clear()

    user = await crud.get_anonim(
        user_id=message.from_user.id
    )
    if user:
        await message.answer(
            text=texts.ANONCHAT_MENU,
            reply_markup=anon_menu()
        )
    else:

        await message.answer(
            text=texts.ANONCHAT_GREETING_NEW_USER
        )
        await message.answer(
            text=texts.ANONCHAT_REGISTRATION_1, 
            reply_markup=registration.gender_select(action='gender')
        )

@router.callback_query(F.data.startswith('gender'))
async def select_gender(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(gender=call.data.split('_')[1])
    
    await call.message.edit_text(
        text=texts.ANONCHAT_REGISTRATION_2,
        reply_markup=registration.select_interests(action='interest')
    )

@router.callback_query(F.data.startswith('interest'))
async def interests_select(call: types.CallbackQuery, state: FSMContext):
    interests = 'Отношения' if call.data.split('_')[1] == 'relationship' else 'Дружба'
    await state.update_data(interests=interests)

    await call.message.edit_text(
        text=texts.ANONCHAT_REGISTRATION_3
        )
    await state.set_state(Registration.select_age)

@router.message(Registration.select_age)
async def choose_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await state.clear()
        return await message.reply('Вы ввели не число!')
        
    if int(message.text) < 14 or int(message.text) > 99: return await message.reply('Возраст не подходит по условиям!')
    info = await state.get_data()

    await crud.create_anon(
        user_id=message.from_user.id,
        gender=info['gender'],
        interests=info['interests'],
        age=int(message.text)
        ) 
    
    await message.answer(
        text='Вы успешно зарегестрировались!'
        )
    await state.clear()
    await message.answer(
            text=texts.ANONCHAT_MENU,
            reply_markup=registration.anon_menu()
        )


