from aiogram import Router, F, Bot, types, html
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext

from database import crud
from keyboards.mandatory_subscription import unsubbed
from keyboards.tests.for_create_test import CANCEL_TEST_TEXT, cancel_test_creation, save_answers
from keyboards.tests.for_test_edit import edit_menu
from keyboards.user_menu import CREATE_TEST_TEXT, user_menu
from states.user import CreateTestSG
from utils import texts
from utils.admin import show_ad_pm, check_follow, show_advert
from utils.telegram import text_len_correct, ad_in_text, upload_photo_to_telegraph


router = Router()


@router.message(F.text == CANCEL_TEST_TEXT, StateFilter(CreateTestSG))
async def cancel_test(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('💼 <b>Меню бота:</b>', reply_markup=user_menu())
    await show_advert(message.from_user.id)

@router.message(Command('new'))
@router.message(F.text == CREATE_TEST_TEXT)
async def handle_command(message: types.Message, state: FSMContext, bot: Bot):
    user = await crud.get_user(message.from_user.id)
    follows = await check_follow(user, bot)

    if follows and "subs" in follows:
        return await message.answer(
            texts.SUB_TEXT,
            reply_markup=unsubbed(follows)
        )

    await state.set_state(CreateTestSG.get_name)
    msg = await message.answer(texts.NAME_DESC, reply_markup=cancel_test_creation())
    await state.update_data(msg_to_delete=msg.message_id)
    await show_advert(message.from_user.id)

@router.callback_query(F.data == 'create_text')
async def handle_command(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await crud.get_user(call.from_user.id)
    follows = await check_follow(user, bot)

    if follows and "subs" in follows:
        return await call.message.answer(
            texts.SUB_TEXT,
            reply_markup=unsubbed(follows)
        )

    await state.set_state(CreateTestSG.get_name)
    msg = await call.message.answer(texts.NAME_DESC, reply_markup=cancel_test_creation())
    await state.update_data(msg_to_delete=msg.message_id)
    await show_advert(call.from_user.id)

@router.message(F.text, CreateTestSG.get_name)
async def get_new_test_name(message: types.Message, state: FSMContext):
    if ad_in_text(message.text):
        return await message.answer(texts.TEXT_CONTAINS_AD)
    if not await text_len_correct(10, 128, message):
        return

    await state.update_data(test_name=html.quote(message.text))
    await state.set_state(CreateTestSG.get_template)

    await message.answer(texts.TEMPLATE_DESC)


@router.message(F.text, CreateTestSG.get_template)
async def get_new_test_template(message: types.Message, state: FSMContext):
    if ad_in_text(message.text):
        return await message.answer(texts.TEXT_CONTAINS_AD)
    if not await text_len_correct(0, 100, message):
        return
    if '***' not in message.text:
        return await message.answer(texts.TEXT_WITHOUT_ELLIPSIS)

    await state.update_data(test_template=html.quote(message.text))
    await state.set_state(CreateTestSG.get_answers)

    await message.answer(texts.ANSWERS_DESC)


@router.message(F.text | (F.photo & F.caption), CreateTestSG.get_answers)
async def get_new_test_answers(message: types.Message, state: FSMContext, bot: Bot):
    text = message.text or message.caption
    photo = None if message.photo is None else message.photo[-1]

    if ad_in_text(text):
        return await message.answer(texts.TEXT_CONTAINS_AD)
    if not await text_len_correct(0, 100, message):
        return

    if photo:
        photo = await upload_photo_to_telegraph(photo, bot)

    state_data = await state.get_data()
    if (answers := state_data.get('answers')) is None:
        await state.update_data(answers=[(html.quote(text), photo)])
    else:
        answers.append((html.quote(text), photo))
        await state.update_data(answers=answers)

    await message.answer(texts.MORE_ANSWERS_DESC, reply_markup=save_answers())


@router.callback_query(F.data == 'save_answers', CreateTestSG.get_answers)
async def save_new_test_answers(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    await state.clear()

    message_to_delete = state_data['msg_to_delete']
    test_name = state_data['test_name']
    test_template = state_data['test_template']
    test_answers = state_data['answers']

    test_id = await crud.create_test(test_name, test_template, test_answers, call.from_user.id)

    try:
        await bot.delete_message(call.from_user.id, message_to_delete)
    except:
        pass

    await call.message.answer(
        texts.MINITEST_DESC.format(
            test_name=test_name,
            pass_counter=0,
            top_counter=test_id
        ),
        reply_markup=edit_menu(test_id)
    )

    await show_advert(call.from_user.id)
