import asyncio
import logging
import time

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from keyboards.admin.admin import (
    main_menu,
    back_to_menu,
    mandatory_subs_list,
    delete_sub,
    current_views_list,
    view_options,
    refresh_notifications_status,
    refs_menu,
    where_to_send_notifications_menu,
    cancel_action,
    generate_or_cancel_ref
)
from keyboards.user_menu import user_menu
from utils.admin import send_formatted_message, gen_random_ref
from states.admin import Notifs
from database import crud
from database.models import Users, Groups, Tests
from database.models import Subs, Referals, Views

notification_status = {'users_all_count': 0, 'users_count': 0, 'all_users': 0, 'chats_all_count': 0, 'chats_count': 0,
                       'all_chats': 0, "notification_type": ""}
new_sub = {"channel_id": None, "url": None, "channel_name": None}


router = Router()
router.message.filter(F.chat.type == 'private')


@router.message(Command('admin'))
async def admin_menu(m: types.Message):
    users_count = await Users.all().count()
    pass_count = await crud.get_overall_pass_counter()
    tests_count = await Tests.all().count()

    await m.answer(
        f"Меню администратора.\n\n"
        f"Пользователей в боте: {users_count}\n"
        f"Всего тестов в боте: {tests_count}\n"
        f"Всего пройдено тестов (раз): {pass_count}",
        reply_markup=main_menu()
    )


@router.callback_query(F.data.startswith('admin'))
async def admin_menu_from_callback(call: types.CallbackQuery):
    users_count = await Users.all().count()
    pass_count = await crud.get_overall_pass_counter()
    tests_count = await Tests.all().count()

    await call.message.answer(
        f"Меню администратора.\n\n"
        f"Пользователей в боте: {users_count}\n"
        f"Всего тестов в боте: {tests_count}\n"
        f"Всего пройдено тестов (раз): {pass_count}",
        reply_markup=main_menu()
    )


@router.callback_query(F.data == 'cancel_admin')
async def exit_panel(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.delete()
    except:
        pass

    await call.message.answer('💼 <b>Меню бота:</b>', reply_markup=user_menu())


@router.callback_query(F.data.startswith('stats'))
async def stats(call: types.CallbackQuery):
    msg = await call.message.edit_text("Собираю статистику, это займёт некоторое время...")
    day_time = int(time.time()) - 86400
    week_time = int(time.time()) - 604800

    daily_regs = await Users.filter(reg_time__gte=day_time).only('id').count()
    weekly_regs = await Users.filter(reg_time__gte=week_time).only("id").count()
    all_users = await Users.filter().only("id").count()

    active_users_daily = await Users.filter(reg_time__lt=day_time, last_active__gt=day_time).only("id").count()

    subbed_users_count = 0
    for user in await Users.filter(subbed=1).only("subbed_count"):
        subbed_users_count += user.subbed_count

    subbed_users_count_daily = 0
    for user in await Users.filter(subbed=1, reg_time__gte=day_time).only("subbed_count"):
        subbed_users_count_daily += user.subbed_count

    subbed_users_count_weekly = 0
    for user in await Users.filter(subbed=1, reg_time__gte=week_time).only("subbed_count"):
        subbed_users_count_weekly += user.subbed_count

    norefs_users = await Users.filter(ref=None).only("id").count()
    norefs_percentage = (norefs_users / all_users) * 100 if norefs_users > 0 else 0
    norefs_users_daily = await Users.filter(ref=None, reg_time__gte=day_time).only("id").count()
    norefs_percentage_daily = (norefs_users_daily / daily_regs) * 100 if norefs_users_daily > 0 else 0
    norefs_users_weekly = await Users.filter(ref=None, reg_time__gte=week_time).only("id").count()
    norefs_percentage_weekly = (norefs_users_weekly / weekly_regs) * 100 if norefs_users_weekly > 0 else 0

    groups = await Groups.all().count()

    text = f"""
📊Статистика:

<code>Пользователей: {all_users}
Саморост: {norefs_users} ({int(round(norefs_percentage, 0))}%)

Всего групп: {groups} 👥

Суточный онлайн: {active_users_daily}
Всего подписались по ОП: {subbed_users_count}

<b>За неделю:</b>
Пользователей: {weekly_regs}
Саморост: {norefs_users_weekly} ({int(round(norefs_percentage_weekly, 0))}%)
Подписываются по ОП: {subbed_users_count_weekly}

<b>За день:</b>
Пользователей: {daily_regs}
Саморост: {norefs_users_daily} ({int(round(norefs_percentage_daily, 0))}%)
Подписываются по ОП: {subbed_users_count_daily}
</code>
"""

    await msg.edit_text(text, reply_markup=back_to_menu(), parse_mode='html')


@router.callback_query(F.data.startswith('subs'))
async def subs(call: types.CallbackQuery):
    all_subs = await Subs.filter()

    text = "\nТекущие ОП:"

    if all_subs:
        for num, sub in enumerate(all_subs, start=1):
            text += f'\n<a href="{sub.url}">{num}. {sub.channel_name}</a> - {sub.subbed} пдп'
    else:
        text += "\nОтсутствуют."

    await call.message.edit_text(
        text,
        reply_markup=mandatory_subs_list(all_subs),
        parse_mode='html',
        disable_web_page_preview=True
    )


@router.callback_query(F.data.startswith('createSubBot'))
async def create_sub_bot(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Notifs.sub_get_bot_url)

    await call.message.answer(
        'Пришлите мне ссылку на бота.\nДля отмены напишите "отмена".'
    )


@router.message(Notifs.sub_get_bot_url)
async def receive_sub_bot_url(message: types.Message, state: FSMContext):
    if message.text and message.text.lower() == 'отмена':
        return await message.answer("Создание ссылки ОП отменено.")

    await state.update_data(url=message.text)
    await state.set_state(Notifs.sub_get_bot_token)
    await message.answer(
        'Теперь пришлите мне токен бота.\nДля отмены напишите "отмена".'
    )


@router.message(Notifs.sub_get_bot_token)
async def receive_sub_bot_token(message: types.Message, state: FSMContext):
    if message.text and message.text.lower() == 'отмена':
        return await message.answer("Создание ссылки ОП отменено.")

    data = await state.get_data()

    if message.text != '0':
        try:
            msbot = Bot(message.text)
        except:
            return await message.answer('Неверный токен.')

        try:
            msbot_name = (await msbot.me()).first_name
        except:
            msbot_name = data['url']
    else:
        msbot_name = data['url']

    await Subs.create(
        url=data['url'],
        channel_id=0,
        token=message.text,
        type='bot',
        channel_name=msbot_name
    )

    await message.answer(
        'Ссылка на ОП успешно добавлена.'
    )


@router.callback_query(F.data.startswith('createSub'))
async def create_sub(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Notifs.create_sub)

    await call.message.edit_text(
        "Пришлите пост с нужного канала. Внимание, бот должен быть администратором данного канала!\n"
        "Для отмены - ''отмена''",
    )


@router.message(Notifs.create_sub)
async def first_step_creation_sub(m: types.Message, state: FSMContext, bot: Bot):
    await state.clear()

    if m.text and m.text.lower() == 'отмена':
        return await m.answer("Создание ссылки ОП отменено.")

    if m.forward_from_chat:
        new_sub['channel_id'] = m.forward_from_chat.id
        new_sub['channel_name'] = m.forward_from_chat.full_name

    try:
        member = await bot.get_chat_member(
            m.forward_from_chat.id, (await bot.me()).id
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        return await m.answer('Бот не админ в данном канале. Попробуйте отправить другой пост.')

    if member.status in {'left', 'kicked'}:
        return await m.answer('Бот не админ в данном канале. Попробуйте отправить другой пост.')

    await m.answer("Теперь отправьте мне ссылку для вступления в канал.")
    await state.set_state(Notifs.create_sub2)


@router.message(Notifs.create_sub2, F.text)
async def second_step_creation_sub(m: types.Message, state: FSMContext):
    await state.clear()

    new_sub['url'] = m.text
    channel_id = 0 if new_sub['channel_id'] is None else new_sub['channel_id']
    await Subs.create(
        url=new_sub['url'],
        channel_id=channel_id,
        channel_name=new_sub['channel_name']
    )
    await m.answer("Ссылка на ОП добавлена.")


@router.callback_query(F.data.startswith('manageSub_'))
async def manage_subs(call: types.CallbackQuery):
    sub = await Subs.filter(id=int(call.data.split("_")[1]))
    reply_markup = None

    if sub:
        sub = sub[0]
        text = (
            f"ОП <b>{sub.channel_name}</b> ({sub.id})\n"
            f"Channel ID: {sub.channel_id}\n"
            f"Ссылка: {sub.url}\n"
            f"Подписалось: {sub.subbed}"
        )
        reply_markup = delete_sub(sub.id)
    else:
        text = "ОП не найден"
    await call.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(F.data.startswith('deleteSub_'))
async def sub_delete(call: types.CallbackQuery):
    sub = await Subs.filter(id=int(call.data.split("_")[1]))
    if sub:
        sub = sub[0]

        await sub.delete()
        await call.message.answer("ОП удалён")
    else:
        await call.message.answer("ОП уже удалён")


@router.callback_query(F.data == 'csv')
async def to_csv(call: types.CallbackQuery):
    await call.message.edit_text("Начинаю выгрузку в csv, это займёт некоторое время...")

    all_users = await Users.filter(valid=1).values_list("id", flat=True)
    all_groups = await Groups.filter(is_active=1).values_list("id", flat=True)

    with open('users.csv', 'w') as f:
        f.write('\n'.join([str(chat_id) for chat_id in all_users + all_groups]))

    await call.message.answer_document(types.FSInputFile('users.csv'))

    await call.message.answer(
        "Выгрузка завершена.\nВ файле:\nЮзеров: {}\nЧатов: {}".format(len(all_users), len(all_groups)),
        reply_markup=back_to_menu()
    )


@router.callback_query(F.data == 'CSV')
async def to_csv_all(call: types.CallbackQuery):
    await call.message.edit_text("Начинаю выгрузку в csv, это займёт некоторое время...")

    all_users = await Users.all().values_list("id", flat=True)
    all_groups = await Groups.all().values_list("id", flat=True)

    with open('users.txt', 'w') as f:
        f.write('\n'.join([str(chat_id) for chat_id in all_users + all_groups]))

    await call.message.answer_document(types.FSInputFile('users.txt'))

    await call.message.answer(
        "Выгрузка завершена.\nВ файле:\nЮзеров: {}\nЧатов: {}".format(len(all_users), len(all_groups)),
        reply_markup=back_to_menu()
    )


@router.callback_query(F.data == 'updateCsv')
async def update_csv(call: types.CallbackQuery, bot: Bot):
    await call.message.edit_text("Обновляю статистику по валиду, это займёт время...\nНачинаю с чатов...\n")

    chats_count = 0
    users_count = 0
    user_to_dict = ""

    allUsers = await Users.filter(valid=1).only("id")
    for user in allUsers:
        try:
            await bot.send_chat_action(user.id, "typing")
            user_to_dict += f"{user.id}\n"
            users_count += 1
            await asyncio.sleep(.15)
        except:
            await Users.filter(id=user.id).update(valid=0)
    with open('users.csv', 'w') as f:
        f.write(user_to_dict)
    await bot.send_document(call.message.chat.id, types.FSInputFile('users.csv'))

    await bot.send_message(
        call.message.chat.id,
        "Выгрузка завершена, присылаю файл. В файле:\nЮзеров: {}\nЧатов: {}".format(users_count, chats_count),
        reply_markup=back_to_menu()
    )


@router.callback_query(F.data == 'deleteInactive')
async def delete_inactive(call: types.CallbackQuery, bot: Bot):
    msg = await bot.edit_message_text(
        "Начинаю удаление, это займёт некоторое время...", call.message.chat.id,
        call.message.message_id
    )

    all_count = 0
    deleted = 0
    valid = 0
    for user in await Users.filter().only("id"):
        if all_count / 500 == all_count // 500:
            try:
                await bot.edit_message_text(
                    "Удаление инактива:\nПройдено: {}\nУдалено: {}\nВалид: {}".format(all_count, deleted, valid),
                    msg.chat.id, msg.message_id)
            except:
                pass
        all_count += 1
        try:
            await bot.send_chat_action(user.id, 'typing')
            valid += 1
            await asyncio.sleep(.3)
        except:
            deleted += 1
            await Users.filter(id=user.id).delete()

    await call.message.answer("Удаление завершено. Всего юзеров: {}\nУдалено: {}\nВалид: {}".format(
        all_count, deleted, valid
    ))


@router.callback_query(F.data.startswith('views'))
async def views(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    all_views = await Views.filter()
    text = "\nТекущие показы:"

    if all_views:
        for view in all_views:
            if view.status == 1:
                status = "ЛС"
            elif view.status == 2:
                status = "В чатах"
            elif view.status == 4:
                status = "В чатах (обнова)"
            else:
                status = "Закончился"
            text += f"\n{view.name} ({status}) - {view.viewed}/{view.max_viewed}"
    else:
        text += "\nОтсутствуют."

    await call.message.edit_text(
        text,
        reply_markup=current_views_list(all_views),
        disable_web_page_preview=True
    )


views_names = ""


@router.callback_query(F.data == 'CreateView')
async def create_view(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Notifs.create_view)
    await call.message.edit_text("Пришлите название показа.", reply_markup=cancel_action('views'))


@router.message(Notifs.create_view)
async def first_step_creation(m: types.Message, state: FSMContext):
    await state.clear()
    if m.text and m.text.lower() == 'отмена':
        return await m.answer("Создание показа отменено")

    global views_names
    views_names = m.text
    await state.set_state(Notifs.create_view2)
    await m.answer("Теперь отправьте мне сообщение для показа", reply_markup=cancel_action('views'))


@router.message(Notifs.create_view2)
async def second_step_creation(m: types.Message, state: FSMContext):
    await state.clear()
    if m.text and m.text.lower() == 'отмена':
        return await m.answer("Создание показа отменено")

    global views_names
    watched_users = [0]
    if m.reply_markup:
        await Views.create(name=views_names, from_user=m.from_user.id, message_id=m.message_id,
                           watched_users=watched_users, markup=m.reply_markup.model_dump(), msg=m.html_text)
    else:
        await Views.create(name=views_names, from_user=m.from_user.id, message_id=m.message_id,
                           watched_users=watched_users, msg=m.html_text)
    await m.answer(
        "Теперь отправьте мне количество показов.",
        reply_markup=cancel_action('views')
    )
    await state.set_state(Notifs.create_view3)


@router.message(Notifs.create_view3, F.text)
async def third_step_creation(m: types.Message, state: FSMContext):
    await state.clear()
    if m.text and m.text.lower() == 'отмена':
        return await m.answer("Создание показа отменено")

    global views_names
    view = (await Views.filter(name=views_names))[0]
    await Views.filter(name=views_names).update(max_viewed=int(m.text), status=1)

    await m.answer("Показ запущен!")


# @dp.callback_query_handler(lambda call: call.data.startswith("createView_"))
# async def createView_(call):
#     if call.data.split("_")[2] == "1":
#         await Views.filter(id=call.data.split("_")[1]).update(status=1)
#     elif call.data.split("_")[2] == "3":
#         await Views.filter(id=call.data.split("_")[1]).update(status=3)
#     await call.message.edit_text("Показ запущен.")


@router.callback_query(F.data.startswith('manageView_'))
async def manage_views(call: types.CallbackQuery):
    view = await Views.filter(id=int(call.data.split("_")[1]))

    if view:
        view = view[0]
        text = f"Показ {view.name}\nID: {view.id}\nПоказано: {view.viewed}\nВсего показов: {view.max_viewed}"
        markup = view_options(view.id)
    else:
        text = "Показ не найден"
        markup = back_to_menu()

    await call.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(F.data.startswith('deleteView_'))
async def view_delete(call: types.CallbackQuery):
    view = await Views.filter(id=int(call.data.split("_")[1]))
    if view:
        view = view[0]

        await view.delete()
        await call.message.answer("Показ удалён")
    else:
        await call.message.answer("Показ уже удалён")


@router.callback_query(F.data.startswith('watchView_'))
async def view_watch(call: types.CallbackQuery):
    view = await Views.filter(id=int(call.data.split("_")[1]))
    if view:
        view = view[0]

        if view.markup:
            await call.message.answer(view.msg, reply_markup=view.markup, parse_mode='html')
            # await bot.copy_message(call.message.chat.id, view.from_user, view.message_id, reply_markup=view.markup)
        else:
            await call.message.answer(view.msg, parse_mode='html')
    else:
        await call.message.answer("Показ удалён.")


@router.callback_query(F.data.startswith('notifications'))
async def notifications(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Куда шлём?", reply_markup=where_to_send_notifications_menu())


@router.callback_query(F.data.startswith('chats_notifications'))
async def chats_notifications(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Создаётся новая рассылка по группам. Пришлите пост.",
        reply_markup=cancel_action('notifications')
    )
    await state.set_state(Notifs.first_step)
    notification_status["notification_type"] = "chats"


@router.callback_query(F.data.startswith('users_notifications'))
async def chats_notifications(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Создаётся новая рассылка по пользователям. Пришлите пост.",
        reply_markup=cancel_action('notifications')
    )
    await state.set_state(Notifs.first_step)
    notification_status["notification_type"] = "users"


@router.callback_query(F.data.startswith('all_notifications'))
async def chats_notifications(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Создаётся новая рассылка по группам и пользователям. Пришлите пост.",
        reply_markup=cancel_action('notifications')
    )
    await state.set_state(Notifs.first_step)
    notification_status["notification_type"] = "all"


@router.message(Notifs.first_step)
async def first_step_notify(m: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    if m.text and m.text.lower() == 'отмена':
        return await m.answer("Рассылка отменена.\nГлавное меню.", reply_markup=main_menu())

    notification_status['users_all_count'] = 0
    notification_status['users_count'] = 0
    notification_status['all_users'] = 0
    notification_status['chats_all_count'] = 0
    notification_status['chats_count'] = 0
    notification_status['all_chats'] = 0
    all_users = await Users.all().only('id').count()
    notification_status['all_users'] = all_users

    await m.answer("Рассылка пошла.", reply_markup=refresh_notifications_status())

    if notification_status["notification_type"] in ["all", "users"]:
        for user in await Users.all().only("id", "first_name", "username"):

            try:
                await send_formatted_message(user.id, m, user.first_name, user.username, bot)
                notification_status['users_count'] += 1
            except Exception as e:
                logging.error(e, exc_info=True)
            finally:
                await asyncio.sleep(.04)

            notification_status['users_all_count'] += 1
    all_chats = await Groups.all().only('id').count()
    notification_status['all_chats'] = all_chats

    if notification_status["notification_type"] in ["all", "chats"]:
        for group in await Groups.all().only("id"):
            try:
                await bot.copy_message(group.id, m.chat.id, m.message_id, reply_markup=m.reply_markup)
                notification_status['chats_count'] += 1
                await asyncio.sleep(.07)
            except:
                pass
            notification_status['chats_all_count'] += 1
    text = f"""
    Всего юзеров в базе: {notification_status['all_users']}
    Пройдено юзеров: {notification_status['users_all_count']}
    Успешно отправлено: {notification_status['users_count']}
    Всего чатов в базе: {notification_status['all_chats']}
    Пройдено чатов: {notification_status['chats_all_count']}
    Успешно отправлено: {notification_status['chats_count']}
    """

    await m.answer("Рассылка завершена. {}".format(text))


@router.callback_query(F.data == 'refreshNotify')
async def refresh_notify(call: types.CallbackQuery):
    text = f"""
Идёт рассылка ({notification_status["notification_type"]}).
Всего юзеров в базе: {notification_status['all_users']}
Пройдено юзеров: {notification_status['users_all_count']}
Успешно отправлено: {notification_status['users_count']}

Всего чатов в базе: {notification_status['all_chats']}
Пройдено чатов: {notification_status['chats_all_count']}
Успешно отправлено: {notification_status['chats_count']}
"""
    await call.message.edit_text(text, reply_markup=refresh_notifications_status())


@router.callback_query(F.data == 'refs')
async def refs(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Подождите...")
    await asyncio.sleep(.3)

    all_refs = await Referals.filter()
    text = "Полученные рефкоды:\n"

    for ref in all_refs:
        try:
            price_all = ref.price / ref.clicked
        except:
            price_all = ref.price
        text += "\n/ref_{} - {}👥 ({}p.)".format(ref.name, ref.clicked, round(price_all, 2))

    await call.message.answer(text, reply_markup=refs_menu())


@router.message(F.text.startswith('/ref_'))
async def ref_look(m: types.Message, bot: Bot):
    result = m.text.replace('/ref_', '', 1)
    refcode = (await Referals.filter(name=result))[0]

    day_time = int(time.time()) - 86400
    week_time = int(time.time()) - 604800

    subbed_users_count = 0
    subbed_alltime = await Users.filter(subbed=1, ref=refcode.name).only("subbed_count")
    for user in subbed_alltime:
        subbed_users_count += user.subbed_count

    subbed_users_count_daily = 0
    subbed_daily = await Users.filter(subbed=1, reg_time__gte=day_time, ref=refcode.name).only("subbed_count")
    for user in subbed_daily:
        subbed_users_count_daily += user.subbed_count

    subbed_users_count_weekly = 0
    subbed_weekly = await Users.filter(subbed=1, reg_time__gte=week_time, ref=refcode.name).only("subbed_count")
    for user in subbed_weekly:
        subbed_users_count_weekly += user.subbed_count

    daily_regs = await Users.filter(reg_time__gte=day_time, ref=refcode.name).count()
    weekly_regs = await Users.filter(reg_time__gte=week_time, ref=refcode.name).count()
    all_users = await Users.filter(ref=refcode.name).count()

    active_users_daily = await Users.filter(
        ref=refcode.name,
        reg_time__lt=day_time,
        last_active__gt=day_time).only("id").count()

    try:
        price_unique = refcode.price / refcode.count
    except:
        price_unique = refcode.price
    try:
        price_all = refcode.price / refcode.clicked
    except:
        price_all = refcode.price

    price_for_all = refcode.price / all_users if all_users > 0 else refcode.price

    non_unique = refcode.clicked - refcode.count
    non_unique_percentage = (non_unique / refcode.clicked) * 100 if non_unique > 0 else 0

    bot_name = (await bot.me()).username

    if all_users != 0:
        alltime_percentage = round(len(subbed_alltime) / all_users * 100, 1)
    else:
        alltime_percentage = 0

    if weekly_regs != 0:
        weekly_percentage = round(len(subbed_weekly) / weekly_regs * 100, 1)
    else:
        weekly_percentage = 0

    if daily_regs != 0:
        daily_percentage = round(len(subbed_daily) / daily_regs * 100, 1)
    else:
        daily_percentage = 0

    text = f"""
📊<b>Статистика:</b>
<code>
Пользователей: {all_users}
Всего подписались по ОП: {len(subbed_alltime)} ({alltime_percentage}%)
Суточный онлайн: {active_users_daily} 

За неделю:
Пользователей: {weekly_regs}
Подписались по ОП: {len(subbed_weekly)} ({weekly_percentage}%)

За день:
Пользователей: {daily_regs}
Подписались по ОП: {len(subbed_daily)} ({daily_percentage}%)
</code>

Цена: {refcode.price}р.
Переходы: {refcode.clicked} ({round(price_all, 2)}p.)
Уникальных: {refcode.count} ({round(price_unique, 2)}p.)

https://t.me/{bot_name}?start={refcode.name}
"""

    await m.answer(text, reply_markup=back_to_menu(), parse_mode='html', disable_web_page_preview=True)


@router.callback_query(F.data == 'delrefs')
async def del_refs(call: types.CallbackQuery):
    all_refs = await Referals.filter()
    text = "Выберите рефкод для удаления:\n"

    for ref in all_refs:
        try:
            price_all = ref.price / ref.clicked
        except:
            price_all = ref.price
        text += "\n/delref_{} - {}👥 ({}p.)".format(ref.name, ref.clicked, round(price_all, 2))

    await call.message.answer(text, reply_markup=cancel_action('refs'))


@router.message(F.text.startswith('/delref_'))
async def del_ref(m: types.Message):
    result = m.text.replace('/delref_', '', 1)
    refcode = (await Referals.filter(name=result))[0]
    await refcode.delete()
    await m.answer("Реферальный код удалён.", reply_markup=back_to_menu(with_cancel=False))


@router.callback_query(F.data == 'createref')
async def create_ref(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Notifs.createref)
    await call.message.edit_text(
        'Отправь цену реферальной ссылки.',
        reply_markup=cancel_action('refs')
    )


@router.message(Notifs.createref, F.text)
async def create_refcode(m: types.Message, state: FSMContext):

    price = int(m.text)
    await state.update_data(ref_price=price)

    await state.set_state(Notifs.createref2)
    await m.answer(
        "<i>Отправьте название ссылки или нажмите кнопку для автоматического создания.</i>",
        reply_markup=generate_or_cancel_ref()
    )


@router.callback_query(Notifs.createref2, F.data == 'gen_ref')
async def gen_refcode(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    ref = gen_random_ref()

    await Referals.create(name=ref, price=data['ref_price'])
    bot_name = (await bot.me()).username
    await call.message.edit_text(
        f"<b>Создана новая реферальная ссылка:</b>\n\n"
        f"Для ЛС: https://t.me/{bot_name}?start={ref}\n"
        f"Для групп: https://t.me/{bot_name}?startgroup={ref}",
        reply_markup=back_to_menu(with_cancel=False)
    )


@router.message(Notifs.createref2, F.text)
async def create_refcode2(m: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    await Referals.create(name=m.text, price=data['ref_price'])
    bot_name = (await bot.me()).username
    await m.answer(
        f"<b>Создана новая реферальная ссылка:</b>\n\n"
        f"Для ЛС: https://t.me/{bot_name}?start={m.text}\n"
        f"Для групп: https://t.me/{bot_name}?startgroup={m.text}",
        reply_markup=back_to_menu(with_cancel=False)
    )
