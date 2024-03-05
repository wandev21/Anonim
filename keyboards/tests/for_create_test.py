from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder


CANCEL_TEST_TEXT = '🚫 Отмена'


def cancel_test_creation() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text=CANCEL_TEST_TEXT)
    return builder.as_markup(resize_keyboard=True)


def save_answers() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='✅ Сохранить',
        callback_data='save_answers'
    )
    return builder.as_markup()
