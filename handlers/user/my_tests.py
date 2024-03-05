from random import choice

from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import crud
from states.user import EditTestSG, ConfirmTestDeleteSG
from utils import texts
from utils.admin import show_ad_pm, check_follow, show_advert
from utils.telegram import ad_in_text, upload_photo_to_telegraph, text_len_correct
from keyboards.user_menu import MY_TESTS_TEXT, user_menu
from keyboards.mandatory_subscription import unsubbed
from keyboards.tests.for_test_edit import (
    EditTestCF,
    DeleteTestCF,
    ConfirmTestDeleteCF,
    ListAnswerVariantsCF,
    AddAnswersCF,
    VariantsToDeleteCF,
    DeleteAnswerCF,
    ChangeCoverCF,
    edit_menu,
    confirm_test_delete_menu,
    add_delete_variants,
    delete_answers_menu,
    back_to_edit,
    my_tests_menu
)


router = Router()


@router.callback_query(F.data == 'return_menu')
async def return_menu(call: types.CallbackQuery):
    try:
        await call.message.delete()
    except:
        pass

    await call.message.answer('💼 <b>Меню бота:</b>', reply_markup=user_menu())


@router.message(Command('mytests'))
@router.message(F.text == MY_TESTS_TEXT)
async def handle_command(message: types.Message, bot: Bot):
    user = await crud.get_user(message.from_user.id)
    follows = await check_follow(user, bot)

    if follows and "subs" in follows:
        return await message.answer(
            texts.SUB_TEXT,
            reply_markup=unsubbed(follows)
        )

    tests = await crud.get_user_tests(message.from_user.id)

    if len(tests) == 0:
        return await message.answer(texts.NO_MY_TESTS_DESC)

    await message.answer(
        texts.MY_TESTS_DESC.format(tests_created=len(tests)),
        reply_markup=my_tests_menu(tests)
    )

    await show_advert(message.from_user.id)


@router.callback_query(F.data == 'tests_list')
async def handle_command(call: types.CallbackQuery):
    tests = await crud.get_user_tests(call.from_user.id)

    if len(tests) == 0:
        return await call.message.edit_text(texts.NO_MY_TESTS_DESC)

    await call.message.edit_text(
        texts.MY_TESTS_DESC.format(tests_created=len(tests)),
        reply_markup=my_tests_menu(tests)
    )
    await show_advert(call.from_user.id)


@router.callback_query(EditTestCF.filter())
async def handle(call: types.CallbackQuery, callback_data: EditTestCF):
    test = await crud.get_test_by_id(callback_data.test_id)
    test_rank = await crud.get_test_rank(test)

    await call.message.edit_text(
        texts.MINITEST_DESC.format(
            test_name=test.name,
            pass_counter=test.pass_counter,
            top_counter=test_rank
        ),
        reply_markup=edit_menu(test.id)
    )


@router.callback_query(ListAnswerVariantsCF.filter())
async def handle(call: types.CallbackQuery, callback_data: ListAnswerVariantsCF, state: FSMContext):
    test = await crud.get_test_by_id(callback_data.test_id)
    answers = await crud.get_answers_by_test_id(callback_data.test_id, only_text=True)

    await call.message.edit_text(
        texts.EDIT_ANSWERS_DESC.format(
            answers=', '.join(answers),
            random_result=test.template.replace('***', choice(answers))
        ),
        reply_markup=add_delete_variants(callback_data.test_id)
    )


@router.callback_query(AddAnswersCF.filter())
async def handle(call: types.CallbackQuery, callback_data: AddAnswersCF, state: FSMContext):
    await state.set_state(EditTestSG.get_answers)
    await state.update_data(test_id=callback_data.test_id)
    await call.message.edit_text(
        'Отправь ответ который нужно добавить',
        reply_markup=back_to_edit(callback_data.test_id)
    )


@router.message(F.text | (F.photo & F.caption), EditTestSG.get_answers)
async def get_new_answers(message: types.Message, state: FSMContext, bot: Bot):
    text = message.text or message.caption
    photo = None if message.photo is None else message.photo[-1]

    if ad_in_text(text):
        return await message.answer(texts.TEXT_CONTAINS_AD)
    if not await text_len_correct(10, 100, message):
        return

    if photo:
        photo = await upload_photo_to_telegraph(photo, bot)

    state_data = await state.get_data()
    test_id = state_data['test_id']
    await crud.add_answer_to_test(test_id, text, photo)

    await message.answer(texts.MORE_ANSWERS_DESC, reply_markup=back_to_edit(test_id))


@router.callback_query(VariantsToDeleteCF.filter())
async def handle(call: types.CallbackQuery, callback_data: VariantsToDeleteCF):
    answers = await crud.get_answers_by_test_id(callback_data.test_id)
    await call.message.edit_text(
        texts.DELETE_ANSWER_DESC,
        reply_markup=delete_answers_menu(answers, callback_data.test_id)
    )


@router.callback_query(DeleteAnswerCF.filter())
async def handle(call: types.CallbackQuery, callback_data: DeleteAnswerCF):
    await crud.delete_answer_by_id(callback_data.answer_id)
    await call.message.edit_text(
        'Вариант успешно удален.',
        reply_markup=back_to_edit(callback_data.test_id)
    )


@router.callback_query(DeleteTestCF.filter())
async def handle(call: types.CallbackQuery, callback_data: DeleteTestCF, state: FSMContext):
    test = await crud.get_test_by_id(callback_data.test_id)
    await state.set_state(ConfirmTestDeleteSG.confirmation)
    await call.message.edit_text(
        texts.DELETE_MINITEST_DESC.format(test_name=test.name),
        reply_markup=confirm_test_delete_menu(test.id)
    )


@router.callback_query(ConfirmTestDeleteCF.filter(), ConfirmTestDeleteSG.confirmation)
async def handle(call: types.CallbackQuery, callback_data: ConfirmTestDeleteCF, state: FSMContext):
    await state.clear()
    await crud.delete_test_by_id(callback_data.test_id)

    try:
        await call.message.delete()
    except:
        pass

    await call.message.answer(
        '💼 <b>Меню бота:</b>',
        reply_markup=user_menu()
    )


@router.callback_query(ChangeCoverCF.filter())
async def handle(call: types.CallbackQuery, callback_data: ChangeCoverCF, state: FSMContext):
    await state.set_state(EditTestSG.get_cover)
    await state.update_data(test_id=callback_data.test_id)
    await call.message.edit_text(
        texts.CHANGE_COVER_DESC,
        reply_markup=back_to_edit(callback_data.test_id)
    )


@router.message(F.photo, EditTestSG.get_cover)
async def get_cover_image_for_test(message: types.Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    await state.clear()

    await crud.update_test_cover_by_id(
        state_data['test_id'],
        await upload_photo_to_telegraph(message.photo[-1], bot)
    )
    await message.answer('✅ Обложка успешно установлена.', reply_markup=back_to_edit(state_data['test_id']))


@router.message(EditTestSG.get_cover)
async def get_cover_image_for_test(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    await message.answer(
        texts.CHANGE_COVER_ERROR_DESC,
        reply_markup=back_to_edit(state_data['test_id'])
    )
