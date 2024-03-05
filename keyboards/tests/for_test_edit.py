from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class EditTestCF(CallbackData, prefix='edit_test'):
    test_id: int


class ChangeCoverCF(CallbackData, prefix='test_cover'):
    test_id: int


class ListAnswerVariantsCF(CallbackData, prefix='test_answers'):
    test_id: int


class AddAnswersCF(CallbackData, prefix='add_new_answers'):
    test_id: int


class VariantsToDeleteCF(CallbackData, prefix='variants_to_delete'):
    test_id: int


class DeleteTestCF(CallbackData, prefix='delete_test'):
    test_id: int


class ConfirmTestDeleteCF(CallbackData, prefix='confirm_test_delete'):
    test_id: int


class DeleteAnswerCF(CallbackData, prefix='delete_answer'):
    test_id: int
    answer_id: int


def back_to_edit(test_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⬅️ Назад',
        callback_data=EditTestCF(test_id=test_id)
    )
    return builder.as_markup()


def my_tests_menu(tests: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for test_id, test_name in tests:
        builder.button(text=test_name, callback_data=EditTestCF(test_id=test_id))

    builder.adjust(2)

    builder.button(
        text='Вернуть меню',
        callback_data='return_menu'
    )

    builder.adjust(1)

    return builder.as_markup()


def edit_menu(test_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='📩 Поделиться',
        switch_inline_query=f'{test_id}'
    )
    builder.button(
        text='🎆 Добавить обложку',
        callback_data=ChangeCoverCF(test_id=test_id)
    )
    builder.button(
        text='🌀 Варианты ответов',
        callback_data=ListAnswerVariantsCF(test_id=test_id)
    )
    builder.button(
        text='❌ Удалить минитест',
        callback_data=DeleteTestCF(test_id=test_id)
    )
    builder.button(
        text='⬅️ Назад',
        callback_data='tests_list'
    )

    builder.adjust(1)
    return builder.as_markup()


def add_delete_variants(test_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='➕ Добавить вариант',
        callback_data=AddAnswersCF(test_id=test_id)
    )
    builder.button(
        text='➖ Удалить вариант',
        callback_data=VariantsToDeleteCF(test_id=test_id)
    )
    builder.button(
        text='⬅️ Назад',
        callback_data=EditTestCF(test_id=test_id)
    )

    builder.adjust(1)
    return builder.as_markup()


def delete_answers_menu(answers: list[tuple[int, str]], test_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for answer_id, answer_text in answers:
        builder.button(text=answer_text, callback_data=DeleteAnswerCF(
            answer_id=answer_id, test_id=test_id))

    builder.adjust(2)

    builder.button(
        text='⬅️ Назад',
        callback_data=EditTestCF(test_id=test_id)
    )

    builder.adjust(1)
    return builder.as_markup()


def confirm_test_delete_menu(test_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Да, удалить',
        callback_data=ConfirmTestDeleteCF(test_id=test_id)
    )

    builder.button(
        text='⬅️ Назад',
        callback_data=EditTestCF(test_id=test_id)
    )

    builder.adjust(1)
    return builder.as_markup()
