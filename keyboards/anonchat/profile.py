from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

def profile_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='ubah usia', callback_data='change_age')
    builder.button(text='ubah jenis kelamin', callback_data='change_gender')
    builder.button(text='sunting obrolan', callback_data='change_chat')

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

