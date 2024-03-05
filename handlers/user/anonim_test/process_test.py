from aiogram import Router, types,  F, Bot
from aiogram.fsm.context import FSMContext

from states.user import AnonTest

from utils import texts

router = Router()

@router.callback_query(F.data.startswith('anontest'))
async def start_test(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = int(call.data.split('_')[1])

    user = await bot.get_chat(chat_id=user_id)
    await call.message.edit_text(
        text=texts.ANONTEST_QUESTION_1.format(user=user.first_name)
    )
    await state.update_data(
        user=user.first_name, 
        user_id=user_id,
        message_id=call.message.message_id
        )
    await state.set_state(AnonTest.question_1)

@router.message(AnonTest.question_1)
async def q_1(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()

    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_2.format(
            user=info['user'],
            ans_1=message.text
        )
    )
    await state.update_data(
            ans_1=message.text
        )
    await state.set_state(AnonTest.question_2)


@router.message(AnonTest.question_2)
async def q_2(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()
    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_3.format(
            user=info['user'],
            ans_1=info['ans_1'],
            ans_2=message.text
        
        )
    )
    await state.update_data(
            ans_2=message.text
        )
    await state.set_state(AnonTest.question_3)


@router.message(AnonTest.question_3)
async def q_3(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()

    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_4.format(
            user=info['user'],
            ans_1=info['ans_1'],
            ans_2=info['ans_2'],
            ans_3=message.text
        )
    )
    await state.update_data(
            ans_3=message.text
        )
    await state.set_state(AnonTest.question_4)

@router.message(AnonTest.question_4)
async def q_4(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()

    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_5.format(
            user=info['user'],
            ans_1=info['ans_1'],
            ans_2=info['ans_2'],
            ans_3=info['ans_3'],
            ans_4=message.text
        )
    )
    await state.update_data(
            ans_4=message.text
        )
    await state.set_state(AnonTest.question_5)

@router.message(AnonTest.question_5)
async def q_5(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()

    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_6.format(
            user=info['user'],
            ans_1=info['ans_1'],
            ans_2=info['ans_2'],
            ans_3=info['ans_3'],
            ans_4=info['ans_4'],
            ans_5=message.text
        )
    )
    await state.update_data(
            ans_5=message.text
        )
    await state.set_state(AnonTest.question_6)


@router.message(AnonTest.question_6)
async def q_6(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()

    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_7.format(
            user=info['user'],
            ans_1=info['ans_1'],
            ans_2=info['ans_2'],
            ans_3=info['ans_3'],
            ans_4=info['ans_4'],
            ans_5=info['ans_5'],
            ans_6=message.text
        )
    )
    await state.update_data(
            ans_6=message.text
        )
    await state.set_state(AnonTest.question_7)


@router.message(AnonTest.question_7)
async def q_7(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()

    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_8.format(
            user=info['user'],
            ans_1=info['ans_1'],
            ans_2=info['ans_2'],
            ans_3=info['ans_3'],
            ans_4=info['ans_4'],
            ans_5=info['ans_5'],
            ans_6=info['ans_6'],
            ans_7=message.text
        )
    )
    await state.update_data(
            ans_7=message.text
        )
    await state.set_state(AnonTest.question_8)


@router.message(AnonTest.question_8)
async def q_8(message: types.Message, state: FSMContext, bot: Bot):
    info = await state.get_data()

    await message.delete()
    
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=info['message_id'],
        text=texts.ANONTEST_QUESTION_9.format(
            user=info['user'],
            ans_1=info['ans_1'],
            ans_2=info['ans_2'],
            ans_3=info['ans_3'],
            ans_4=info['ans_4'],
            ans_5=info['ans_5'],
            ans_6=info['ans_6'],
            ans_7=info['ans_7'],
            ans_8=message.text
        )
    )
    await bot.send_message(
        chat_id=info['user_id'],
        text=texts.ANONTEST_RESULT.format(
            ans_1=info['ans_1'],
            ans_2=info['ans_2'],
            ans_3=info['ans_3'],
            ans_4=info['ans_4'],
            ans_5=info['ans_5'],
            ans_6=info['ans_6'],
            ans_7=info['ans_7'],
            ans_8=message.text
        )
    )
    await state.clear()


