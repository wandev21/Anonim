from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class RateTestCF(CallbackData, prefix="rate"):
    value: int
    test_id: int


def self_chat_rate_menu(test_id: int):
    builder = InlineKeyboardBuilder()
    for num in range(1, 5 + 1):
        builder.button(
            text=f'⭐ {num}',
            callback_data=RateTestCF(value=num, test_id=test_id)
        )
    builder.adjust(5)
    return builder.as_markup()


def group_rate_menu(test_id: int, bot_username: str):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='💥 Пройти',
        switch_inline_query_current_chat=''
    )
    builder.button(
        text='🧩 Создать тест',
        callback_data='create_text'
    )
    builder.adjust(2)

    builder.button(
        text='👥 Добавить в чат',
        url=f'https://t.me/{bot_username}?startgroup='
    )
    builder.button(
        text='⭐ Оценить тест',
        url=f'https://t.me/{bot_username}?start=rate_{test_id}'
    )
    builder.adjust(1)

    return builder.as_markup()
