from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder


def top_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔝 Лучшие тесты', switch_inline_query_current_chat='')
    return builder.as_markup()
