from aiogram import Router, F, Bot, types

from database import crud
from utils.telegram import get_test_result_article
from keyboards.tests.for_test_pass import group_result_menu, register_in_bot_menu


router = Router()


@router.inline_query(lambda query: query.query.isdecimal())
async def show_top_tests(query: types.InlineQuery, bot: Bot):
    test = await crud.get_test_by_id(test_id=int(query.query), prefetch_answers=True)
    user = await crud.get_user(query.from_user.id)

    results = []
    if test is not None:
        results.append(
            get_test_result_article(
                test,
                reply_markup=(
                    group_result_menu(test.id, (await bot.me()).username)
                    if user is not None
                    else register_in_bot_menu((await bot.me()).username)
                ),
                user_in_db=user is not None
            )
        )
        to_exclude = {test.id}
    else:
        to_exclude = set()

    offset = int(query.offset) if query.offset else 0
    tests = await crud.get_all_tests_ranked(
        prefetch_answers=True, offset=offset, exclude_tests=to_exclude, how_many=50 - len(to_exclude)
    )

    kwargs = {}
    if offset >= 50:
        kwargs.update(next_offset=str(offset + 50))
        if len(results) > 0:
            del results[0]  # remove searched test if user scrolled to next offset

    results.extend(
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
    )
    # if query.chat_type == 'sender':
    #     result = get_test_result_article(test, reply_markup=self_chat_rate_menu(test.id))
    # else:
    await query.answer(results, cache_time=5, is_personal=True, **kwargs)
