import logging
import secrets
import random

from aiohttp import ClientSession, FormData

from aiogram import Bot, exceptions
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    PhotoSize,
    Message,
    InputTextMessageContent,
    InlineQueryResultArticle,
    InlineKeyboardMarkup
)
from aiogram.utils.markdown import hide_link

from database.models import Tests
from config import ADMINS
from . import texts


async def set_commands(bot: Bot):
    ru = [
        BotCommand(command='start', description='В начало'),
        BotCommand(command='menu', description='Меню бота'),
        BotCommand(command='mytests', description='Мои тесты'),
        BotCommand(command='new', description='Создать новый тест'),
        # BotCommand(command='test', description='Категории тестов'),
        BotCommand(command='help', description='Помощь'),
    ]
    ru_adm = [
        BotCommand(command='admin', description='Админ панель'),
        BotCommand(command='populate_tests', description='Добавить тесты с помощью файла')
    ]
    ru_adm.extend(ru)

    await bot.set_my_commands(
        commands=ru,
    )
    for admin in ADMINS:
        try:
            await bot.set_my_commands(
                commands=ru_adm,
                scope=BotCommandScopeChat(type='chat', chat_id=admin)
            )
        except exceptions.TelegramAPIError as e:
            logging.error(f'ON SET COMMANDS: {e}')


async def upload_photo_to_telegraph(photo: PhotoSize, bot: Bot) -> str:
    url = 'https://telegra.ph/upload'

    photo_path = await bot.get_file(photo.file_id)
    photo = await bot.download_file(photo_path.file_path)

    form = FormData(quote_fields=False)
    form.add_field(secrets.token_urlsafe(8), photo, content_type='image/jpg')

    async with ClientSession() as session:
        async with session.post(url, data=form) as response:
            endpoint = (await response.json())[0]['src']
            return f'https://telegra.ph{endpoint}'


async def text_len_correct(len_min: int, len_max: int, message: Message):
    text = message.text or message.caption
    if len(text) > len_max:
        await message.answer(texts.TEXT_TOO_LONG)
        return False
    if len(text) < len_min:
        await message.answer(texts.TEXT_TOO_SHORT)
        return False

    return True


def ad_in_text(text: str):
    ad_entities = {'@', 't.me', 'http'}
    return any(entity in text for entity in ad_entities)


def get_text_for_test(test: Tests, user_in_db: bool = True):
    if user_in_db:
        random_answer = random.choice(test.answers)
        if random_answer.cover_img_url:
            cover_url = hide_link(random_answer.cover_img_url)
        else:
            cover_url = ''
        wrapped_answer = f'<b>{random_answer.text}</b>'
        message_text = f'{cover_url}{test.template.replace("***", wrapped_answer)}'
    else:
        message_text = f'<b>Чтобы пройти тест, зарегистрируйтесь в боте 😌</b>'

    return message_text


def get_test_result_article(test: Tests, reply_markup: InlineKeyboardMarkup = None, user_in_db: bool = True):
    message_text = get_text_for_test(test, user_in_db)

    return InlineQueryResultArticle(
        id=str(test.id),
        title=test.name,
        description=f'Использовали: {test.pass_counter}',
        input_message_content=InputTextMessageContent(
            message_text=message_text,
            parse_mode='HTML'
        ),
        thumbnail_url=test.cover_img_url,
        reply_markup=reply_markup
    )
