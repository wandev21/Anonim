from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from database import crud
from keyboards.anonchat.profile import profile_menu
from keyboards.anonchat import registration

from states.user import Registration

from utils import texts

from filters.blockcommands import BlockCommandInConversaton

router = Router()

@router.message(F.text == '👤 Мой профиль', BlockCommandInConversaton())
async def show_profile(message: types.Message):
    user = await crud.get_anonim(
        user_id=message.from_user.id
    )

    name = message.from_user.full_name
    age = user.age
    gender = '🧑🏼‍🦰Парень' if user.gender == 'male' else '👩🏻‍🦰Девушка'
    interests = 'Отношения' if user.interests == 'relationship' else 'Дружба'

    await message.answer(
        text=texts.ANONCHAT_PROFILE.format(
            name=name,
            age=age,
            gender=gender,
            interests=interests
        ),
        reply_markup=profile_menu()
    )

@router.callback_query(F.data == 'change_age')
async def change_chat(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='<i>Напиши, cколько тебе лет? (от 10 до 99)</i>'
        )
    await state.set_state(Registration.change_age)

@router.message(Registration.change_age)
async def choose_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): 
        await state.clear()
        return await message.reply('Вы ввели не число!')
    if int(message.text) < 14 or int(message.text) > 99: return await message.reply('Возраст не подходит по условиям!')

    await crud.change_age(
        user_id=message.from_user.id,
        age=int(message.text)
    )

    user = await crud.get_anonim(
        user_id=message.from_user.id
    )

    name = message.from_user.full_name
    age = user.age
    gender = '🧑🏼‍🦰Парень' if user.gender == 'male' else '👩🏻‍🦰Девушка'
    interests = 'Отношения' if user.interests == 'relationship' else 'Дружба'

    await message.answer(
        text=texts.ANONCHAT_PROFILE.format(
            name=name,
            age=age,
            gender=gender,
            interests=interests
        ),
        reply_markup=profile_menu()
    )

@router.callback_query(F.data == 'change_gender')
async def change_gender(call: types.CallbackQuery):
    await call.message.edit_text(
        text='<i>Выбери ниже, какого ты пола?</i>',
        reply_markup=registration.gender_select(action='edit-gender')
    )

@router.callback_query(F.data.startswith('edit-gender'))
async def get_gender(call: types.CallbackQuery):
    await crud.change_gender(
        user_id=call.from_user.id,
        gender=call.data.split('_')[1]
    )
    user = await crud.get_anonim(
        user_id=call.from_user.id
    )

    name = call.from_user.full_name
    age = user.age
    gender = '🧑🏼‍🦰Парень' if user.gender == 'male' else '👩🏻‍🦰Девушка'
    interests = 'Отношения' if user.interests == 'relationship' else 'Дружба'

    await call.message.edit_text(
        text=texts.ANONCHAT_PROFILE.format(
            name=name,
            age=age,
            gender=gender,
            interests=interests
        ),
        reply_markup=profile_menu()
    )

@router.callback_query(F.data == 'change_chat')
async def change_chat(call: types.CallbackQuery):
    await call.message.edit_text(
        text='<i>Выбери ниже, что тебя интересует?</i>',
        reply_markup=registration.select_interests(action='edit-interest')
    )

@router.callback_query(F.data.startswith('edit-interest'))
async def get_gender(call: types.CallbackQuery):
    await crud.change_interests(
        user_id=call.from_user.id,
        interests=call.data.split('_')[1]
    )
    user = await crud.get_anonim(
        user_id=call.from_user.id
    )

    name = call.from_user.full_name
    age = user.age
    gender = '🧑🏼‍🦰Парень' if user.gender == 'male' else '👩🏻‍🦰Девушка'
    interests = 'Отношения' if user.interests == 'relationship' else 'Дружба'

    await call.message.edit_text(
        text=texts.ANONCHAT_PROFILE.format(
            name=name,
            age=age,
            gender=gender,
            interests=interests
        ),
        reply_markup=profile_menu()
    )