from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

remove_kb = ReplyKeyboardRemove()

def gender_select(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='👩🏻‍🦰wanita', callback_data=f'{action}_girl')
    builder.button(text='🧑🏼‍🦰laki-laki', callback_data=f'{action}_male')

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def select_interests(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='hubungan', callback_data=f'{action}_relationship')
    builder.button(text='persahabatan', callback_data=f'{action}_friendship')

    return builder.as_markup(resize_keyboard=True)

