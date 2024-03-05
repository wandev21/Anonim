from aiogram import Router, types,  F, Bot
from aiogram.fsm.context import FSMContext

from database import crud

from keyboards import default_test

from utils import texts

router = Router()

@router.callback_query(F.data.startswith('startpassdeftest'))
async def start_passing(call: types.CallbackQuery, state: FSMContext):
    test_type = call.data.split('_')[1]
    owner = int(call.data.split('_')[2])
    
    await call.message.edit_text(
        text=texts.DEFAULT_TESTS_PASSING[test_type][0],
        reply_markup=default_test.answers(
            test_type=test_type,
            options=texts.DEFAULT_ANS[test_type][0],
            q_index=0,
            action='ans'
        )
    )

    await state.update_data(answers=[], owner=owner)

@router.callback_query(F.data.startswith('ans'))
async def take_answer(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    test_type = call.data.split('_')[1]
    question_index = call.data.split('_')[2]
    ans_index = call.data.split('_')[3]

    try:
        info = await state.get_data()

        is_right, ans = await crud.is_right_ans(
            user_id=info['owner'],
            test_type=test_type,
            index=int(question_index),
            ans_index=int(ans_index)
        )
        right_or_not = ''
        if is_right:
            right_or_not = '👍 Правильно'
        else:
            right_or_not = f'😢 Неправильно, правильный ответ - {texts.DEFAULT_ANS[test_type][int(question_index)][int(ans)]}'
        await call.message.edit_text(
            text=texts.DEFAULT_TESTS_PASSING[test_type][int(question_index)+1].format(
                right_or_not=right_or_not
            ),
            reply_markup=default_test.answers(
                test_type=test_type,
                options=texts.DEFAULT_ANS[test_type][int(question_index)+1],
                q_index=int(question_index) + 1,
                action='ans'
            )
        )
        upd_answers = info['answers']
        upd_answers.append(ans_index)

        await state.update_data(answers=upd_answers)
    except IndexError:
        info = await state.get_data()
        ans_id, righ_count = await crud.create_answer(
            user_id=call.from_user.id,
            owner=info['owner'],
            test_type=test_type,
            answers=info['answers']
        )
        user = await bot.get_chat(chat_id=info['owner'])
        is_right, ans = await crud.is_right_ans(
            user_id=info['owner'],
            test_type=test_type,
            index=int(question_index) - 1,
            ans_index=int(ans_index)
        )
        right_or_not = ''
        if is_right:
            right_or_not = '👍 Правильно'
        else:
            right_or_not = f'😢 Неправильно, правильный ответ - {texts.DEFAULT_ANS[test_type][int(question_index)-1][int(ans)]}'

        percent = int(righ_count*100/(int(question_index)+1))
        await call.message.edit_text(
            text=texts.RESULT_PASSING.format(
                right_or_not=right_or_not,
                name=user.first_name,
                test_name=texts.DEFAULT_TESTS_NAMES[test_type],
                righ_count=righ_count,
                quantity=int(question_index)+1,
                percent=percent
            )
        )
        
        await bot.send_message(
            chat_id=info['owner'],
            text=texts.SEND_RESULT.format(
                name=call.from_user.first_name,
                test_name=texts.DEFAULT_TESTS_NAMES[test_type],
                percent=percent
            )
        )

