from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardBuilder


CREATE_TEST_TEXT = '🧩 Создать тест'
MY_TESTS_TEXT = '🌟 Мои тесты'
CATALOGUE_TEXT = '🗂 Каталог'
TOP_TEXT = '🔝 Топ тестов'
RANDOM_TEST_TEXT = '🎲 Случайный тест'
ANONIM_TEXT = '✉️ Анонимный чат'
ANONIM_TEST_TEXT = '📨 Анонимные опросы'
DEFAULT_TESTS = '📋 Тесты'


def user_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for text in (CREATE_TEST_TEXT, MY_TESTS_TEXT, TOP_TEXT, RANDOM_TEST_TEXT, ANONIM_TEXT, ANONIM_TEST_TEXT, DEFAULT_TESTS):
        builder.button(text=text)

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def anon_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text='🔎 Найти собеседника')
    builder.button(text='👤 Мой профиль')
    builder.button(text='🔙Назад')
    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)

def anon_test(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='Пройти опрос', callback_data=f'anontest_{user_id}')

    return builder.as_markup(resize_keyboard=True)

def cancel_anon_test() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='❌ Отменить прохождение опроса', callback_data='anonstop')

    return builder.as_markup(resize_keyboard=True)