from aiogram import Router, types,  F, Bot
from aiogram.fsm.context import FSMContext

from database import crud

from keyboards import default_test

from utils import texts

router = Router()

@router.callback_query(F.data.startswith('startdeftest'))
@router.callback_query(F.data.startswith('changeans'))
async def start_creating(call: types.CallbackQuery, state: FSMContext):
    test_type = call.data.split('_')[1]
    await call.message.edit_text(
        text=texts.DEFAULT_TESTS[test_type][0],
        reply_markup=default_test.answers(
            test_type=test_type,
            options=texts.DEFAULT_ANS[test_type][0],
            q_index=0,
            action='create'
        )
    )
    await state.update_data(answers=[])

@router.callback_query(F.data.startswith('create'))
async def take_answer(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    test_type = call.data.split('_')[1]
    question_index = call.data.split('_')[2]
    ans_index = call.data.split('_')[3]
    try:
        info = await state.get_data()
        await call.message.edit_text(
            text=texts.DEFAULT_TESTS[test_type][int(question_index)+1],
            reply_markup=default_test.answers(
                test_type=test_type,
                options=texts.DEFAULT_ANS[test_type][int(question_index)+1],
                q_index=int(question_index) + 1,
                action='create'
            )
        )
        upd_answers = info['answers']
        upd_answers.append(ans_index)

        await state.update_data(answers=upd_answers)
    except IndexError: 
        info = await state.get_data()

        answers = info['answers']
        is_created = await crud.get_or_create_test(
            user_id=call.from_user.id,
            answers=answers,
            test_type=test_type
        )
        me = await bot.me()

        if is_created:
            await call.message.edit_text(
                text=texts.TEST_CREATED.format(
                    q_count=int(question_index) + 1,
                    bot_username=me.username,
                    test_type=test_type,
                    user_id=call.from_user.id
                )
            )
        else:
            await call.message.edit_text(
                text=texts.TEST_EDITED.format(
                    q_count=int(question_index) + 1,
                    bot_username=me.username,
                    test_type=test_type,
                    user_id=call.from_user.id
                )
            )

        

