import time
import logging
import pytz

from typing import Optional, Union
from datetime import datetime, timedelta

from tortoise import connections
from tortoise.contrib.postgres.functions import Random
from tortoise.expressions import F, Q
from tortoise.functions import Sum
from tortoise.transactions import in_transaction
from tortoise.exceptions import OperationalError

from .models import Users, Referals, Tests, Answers, Groups, Subs, Greetings, AnonChat, DefaultTests, DefaultAnswers
from utils.texts import USERS_CATEGORY


async def create_user(
        user_id: int,
        first_name: str,
        username: Optional[str],
        source: Optional[str]
) -> tuple["Users", bool]:
    user = await Users.get_or_none(id=user_id)
    if user:
        return user, False

    if source:
        ref_checker = await Referals.exists(name=source)
    else:
        ref_checker = None

    if ref_checker:
        user = await Users.create(
            id=user_id, first_name=first_name, username=username,
            ref=source, reg_time=int(time.time()),
            last_started=int(time.time())
        )
        await Referals.filter(name=source).update(clicked=F('clicked') + 1, count=F('count') + 1)
    else:
        user = await Users.create(
            id=user_id, first_name=first_name,
            reg_time=int(time.time()),
            last_started=int(time.time()),
        )

    return user, True


async def create_test(
        test_name: str,
        test_template: str,
        test_answers: list[tuple[str, Optional[str]]],
        owner_id: int = None,
        category: str = None
) -> int:
    try:
        async with in_transaction() as conn:
            test = await Tests.create(
                name=test_name,
                template=test_template,
                category=category or USERS_CATEGORY,
                owner_id=owner_id,
                using_db=conn
            )
            answers = [
                Answers(
                    text=text, cover_img_url=img_url, test=test
                ) for text, img_url in test_answers
            ]
            await Answers.bulk_create(answers, using_db=conn)
            return test.id
    except OperationalError as e:
        logging.error(e, exc_info=True)


async def create_group(group_id: int, title: str, username: str = None, source: str = None):
    group = await Groups.get_or_none(id=group_id)
    if group:
        if source:
            minute_ago = datetime.now(tz=pytz.timezone('Europe/Moscow')) - timedelta(minutes=1)
            if group.created_at >= minute_ago:
                group.ref = source if group.ref is None else group.ref
                await group.save()
        return False, group

    group = await Groups.create(
        id=group_id,
        title=title,
        username=username,
        ref=source
    )
    return True, group


async def get_user(user_id: int) -> Optional[Users]:
    return await Users.get_or_none(id=user_id)


async def get_test_by_id(test_id: int, prefetch_answers: bool = False) -> Optional[Tests]:
    test = await Tests.get_or_none(id=test_id)
    if prefetch_answers and test is not None:
        await test.fetch_related('answers')
    return test


async def get_random_test() -> Optional[Tests]:
    return await Tests.annotate(order=Random()).order_by('order').first().prefetch_related('answers')


async def get_test_rank(test: Tests) -> int:
    position = await Tests.filter(pass_counter__gte=test.pass_counter).count()
    return position


async def get_answers_by_test_id(
        test_id: int, only_text: bool = False) -> Union[list[str], list[tuple[int, str]]]:
    if only_text:
        answers = await Answers.filter(test_id=test_id).values_list('text', flat=True)
    else:
        answers = await Answers.filter(test_id=test_id).values_list('id', 'text')
    return answers


async def increment_pass_counter(test_id: int):
    await Tests.filter(id=test_id).update(pass_counter=F('pass_counter') + 1)


async def get_overall_pass_counter() -> int:
    return (
        await Tests
        .all()
        .annotate(overall_passes=Sum('pass_counter'))
        .values_list('overall_passes', flat=True)
    )[0]


async def update_test_cover_by_id(test_id: int, cover_img_url: str) -> None:
    await Tests.filter(id=test_id).update(cover_img_url=cover_img_url)


async def update_sub_counter(user_id: int):
    subs_count = await Subs.filter().only("id").count()
    await Users.filter(id=user_id).update(subbed=1, subbed_count=F('subbed_count') + subs_count)
    await Subs.filter().update(subbed=F('subbed') + 1)


async def delete_test_by_id(test_id: int) -> None:
    await Tests.filter(id=test_id).delete()


async def delete_answer_by_id(answer_id: int) -> None:
    await Answers.filter(id=answer_id).delete()


async def add_answer_to_test(test_id: int, text: str, cover_img_url: str):
    await Answers.create(
        test_id=test_id,
        text=text,
        cover_img_url=cover_img_url
    )


async def add_tests_and_answers_from_parser(tests: list[dict]):
    success_tests = 0
    success_answers = 0
    error_tests = 0

    for test in tests:
        try:
            async with in_transaction() as conn:
                inserted_test = await Tests.create(
                    name=test['test_name'],
                    template=test['template'],
                    category=test['cat'],
                    cover_img_url=test['cover_url'],
                    using_db=conn
                )
                answers = [
                    Answers(
                        text=answer['text'], cover_img_url=answer['cover_url'], test=inserted_test
                    ) for answer in test['answers']
                ]
                answers = await Answers.bulk_create(answers, using_db=conn)

                success_tests += 1
                success_answers += len(answers)

        except OperationalError as e:
            error_tests += 1
            logging.error(e, exc_info=True)

    return success_tests, success_answers, error_tests


async def get_user_tests(user_id: int) -> list[tuple[int, str]]:
    tests = await Tests.filter(owner_id=user_id).values_list('id', 'name')
    return tests


async def get_all_categories() -> list[str]:
    return await Tests.filter(category__not=USERS_CATEGORY).distinct().values_list('category', flat=True)


async def get_all_tests_ranked(
        prefetch_answers: bool = False,
        offset: int = 1,
        how_many: int = 50,
        exclude_tests: set[int] = None
) -> list[Tests]:
    kwargs = {}
    if exclude_tests:
        kwargs.update(id__not_in=exclude_tests)

    if prefetch_answers:
        tests = (
            await Tests
            .filter(**kwargs)
            .order_by('-pass_counter')
            .offset(offset)
            .limit(how_many)
            .prefetch_related('answers')
        )
    else:
        tests = await Tests.filter(
            category__not=USERS_CATEGORY
        ).offset(offset).limit(how_many).order_by('-pass_counter')
    return tests


async def get_tests_by_category_ranked(
        category: str,
        prefetch_answers: bool = False,
        offset: int = 1,
        how_many: int = 50
) -> list[Tests]:
    if category == USERS_CATEGORY:
        return []

    if prefetch_answers:
        tests = await Tests.filter(
            category=category
        ).order_by(
            '-pass_counter'
        ).offset(offset).limit(how_many).prefetch_related('answers')
    else:
        tests = await Tests.filter(
            category=category
        ).offset(offset).limit(how_many).order_by('-pass_counter')
    return tests


async def greeting_exists() -> bool:
    greeting = await Greetings.filter().count()
    return bool(greeting)


async def get_greeting() -> Optional[Greetings]:
    return await Greetings.all().first()


async def create_greeting(text: str, markup: list) -> None:
    await Greetings.all().delete()
    await Greetings.create(
        text=text,
        markup=markup
    )


async def delete_greeting() -> None:
    await Greetings.all().delete()

# anonchat
    
async def get_anonim(user_id: int) -> Optional[AnonChat]:
    return await AnonChat.get_or_none(user_id=user_id)

async def create_anon(
        user_id: int,
        gender: str,
        interests: str,
        age: int
) -> tuple["AnonChat", bool]:
    user = await AnonChat.get_or_none(user_id=user_id)
    if user:
        return user, False

    user = await AnonChat.create(
        user_id=user_id,
        gender=gender,
        interests=interests,
        age=age,
        status='default'
    )

    return user, True
    
async def change_gender(
        user_id: int, 
        gender: str
        ):
    await AnonChat.filter(user_id=user_id).update(gender=gender)

async def change_interests(
        user_id: int, 
        interests: str
        ):
    await AnonChat.filter(user_id=user_id).update(interests=interests)

async def change_age(
        user_id: int, 
        age: int
        ):
    await AnonChat.filter(user_id=user_id).update(age=age)

async def start_conversation(
        user_id: int
        ):
    partner = await AnonChat.get_or_none(status='insearch')

    if partner:
        await AnonChat.filter(user_id=user_id).update(status='inconversation', partner_id=partner.user_id)
        await AnonChat.filter(user_id=partner.user_id).update(status='inconversation', partner_id=user_id)
        return True
    else:
        await AnonChat.filter(user_id=user_id).update(status='insearch')
        return False
    
async def stop_conversation(
        user_id: int, 
        partner_id: int
        ):
    await AnonChat.filter(user_id=user_id).update(status='default', partner_id=None)
    await AnonChat.filter(user_id=partner_id).update(status='default', partner_id=None)

async def set_default_status(
        user_id: int
        ):
    await AnonChat.filter(user_id=user_id).update(status='default')

async def get_default_test_quantity(
        user_id: int
    ):
    quantity = await DefaultTests.filter(owner=user_id)
    return quantity

async def get_or_create_test(
        user_id,
        test_type,
        answers
        ):
    test = await DefaultTests.get_or_none(owner=user_id, test_type=test_type)

    if test:
        await DefaultTests.filter(owner=user_id).update(answers=answers)
        return False

    await DefaultTests.create(
        owner=user_id,
        test_type=test_type,
        answers=answers
    )
    return True

async def is_right_ans(
        user_id,
        test_type,
        index,
        ans_index
    ):
    answers = await DefaultTests.get(owner=user_id, test_type=test_type)

    return int(answers.answers[index]) == int(ans_index), answers.answers[index]
        

async def create_answer(
        user_id,
        owner,
        answers,
        test_type
    ):
    new_ans = await DefaultAnswers.create(
        answered=user_id,
        owner=owner,
        test_type=test_type,
        answers=answers
    )

    right_ans = await DefaultTests.get(owner=owner, test_type=test_type)
    right_count = 0
    for i,j in enumerate(right_ans.answers, 0):
        if j == answers[i]:
            right_count+=1
    
    return new_ans.id, right_count