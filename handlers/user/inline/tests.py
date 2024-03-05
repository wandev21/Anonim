from aiogram import Router, F, Bot, types

from database import crud
from utils.telegram import get_test_result_article
from keyboards.tests.for_test_pass import group_result_menu, register_in_bot_menu


router = Router()


@router.inline_query()
async def show_top_tests(query: types.InlineQuery, bot: Bot):
    offset = int(query.offset) if query.offset else 0
    if len(query.query) > 3:
        tests = await crud.get_tests_by_category_ranked(
            query.query, prefetch_answers=True, offset=offset
        )
    else:
        tests = await crud.get_all_tests_ranked(prefetch_answers=True, offset=offset)

    chat_type_sender = query.chat_type == 'sender'

    kwargs = {}
    if len(tests) >= 50:
        kwargs.update(next_offset=str(offset + 50))

    user = await crud.get_user(query.from_user.id)
    await query.answer(
        [
            get_test_result_article(
                test,
                reply_markup=(
                    group_result_menu(test.id, (await bot.me()).username)
                    if user is not None
                    else register_in_bot_menu((await bot.me()).username)
                ),
                user_in_db=user is not None
            ) for test in tests
        ],
        cache_time=5, is_personal=True,
        **kwargs
    )
