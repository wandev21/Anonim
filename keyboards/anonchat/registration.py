from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

remove_kb = ReplyKeyboardRemove()

def gender_select(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='👩🏻‍🦰Девушка', callback_data=f'{action}_girl')
    builder.button(text='🧑🏼‍🦰Парень', callback_data=f'{action}_male')

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def select_interests(action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='Отношения', callback_data=f'{action}_relationship')
    builder.button(text='Дружба', callback_data=f'{action}_friendship')

    return builder.as_markup(resize_keyboard=True)

