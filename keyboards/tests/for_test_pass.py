from aiogram.utils.keyboard import InlineKeyboardBuilder


def group_result_menu(test_id: int, bot_username: str):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='💥 Пройти',
        switch_inline_query_current_chat=f'{test_id}'
    )
    builder.button(
        text='🧩 Создать тест',
        url=f'https://t.me/{bot_username}'
    )
    builder.adjust(2)

    builder.button(
        text='👥 Добавить в чат',
        url=f'https://t.me/{bot_username}?startgroup=test_kb'
    )
    builder.adjust(1)

    return builder.as_markup()


def register_in_bot_menu(bot_username: str):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='📱 Зарегистрироваться',
        url=f'https://t.me/{bot_username}'
    )

    return builder.as_markup()
