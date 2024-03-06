from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def greetings_menu(greeting_exist: bool = True):
    builder = InlineKeyboardBuilder()

    add_text = '🔄 mengganti' if greeting_exist else '➕ menambahkan'
    builder.button(
        text=add_text,
        callback_data='change_greeting'
    )

    if greeting_exist:
        builder.button(
            text='➖ menghapus',
            callback_data='del_greeting'
        )
        builder.button(
            text='👁 menunjukkan',
            callback_data='reveal_greeting'
        )

    builder.adjust(2)

    builder.button(
        text='🔙 kembali',
        callback_data="admin"
    )

    builder.adjust(1)

    return builder.as_markup()
