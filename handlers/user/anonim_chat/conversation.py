from aiogram import Router, Bot, types,  F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import crud

from keyboards.anonchat import registration
from keyboards.user_menu import anon_menu


from utils import texts

from filters.inconversationfilter import InConversationFilter
from filters.blockcommands import BlockCommandInConversaton

router = Router()


@router.message(F.text == '🔎 Найти собеседника', BlockCommandInConversaton())
async def conversation_start(message: types.Message, state: FSMContext, bot: Bot):
    result = await crud.start_conversation(
        user_id=message.from_user.id
    )
    user = await crud.get_anonim(
        user_id=message.from_user.id
    )

        # начало беседы
    if result:
        await message.answer(
            text=texts.ANONCHAT_START_CONVERSATION,
            reply_markup=registration.remove_kb
            
        )
        await bot.send_message(
            chat_id=user.partner_id,
            text=texts.ANONCHAT_START_CONVERSATION,
            reply_markup=registration.remove_kb
        )

    else:
        await message.answer('<i>Поиск собеседника...</i>\n\n/stop - для прекращения',reply_markup=registration.remove_kb)

@router.message(Command('stop'))
async def stop_chat(message: types.Message, bot: Bot):
    user = await crud.get_anonim(
        user_id=message.from_user.id
    )
    if user.status == 'default': return await message.answer('<i>Вы не находитесь в чатe!</i>')
    if user.status == 'insearch':
        await crud.set_default_status(
            user_id=user.user_id
        )
        return await message.answer(
        text='<b><i>Вы завершили поиск.</i></b>',
        reply_markup=anon_menu()
    )

    await crud.stop_conversation(
        user_id=message.from_user.id,
        partner_id=user.partner_id
    )


    await message.answer(
        text='<b><i>Вы завершили общение.</i></b>',
        reply_markup=anon_menu()
    )

    await bot.send_message(
            chat_id=user.partner_id,
            text='<b><i>Собеседник завершил общение.</i></b>',
            reply_markup=anon_menu()
        )

@router.message(Command('next'))
async def next_opponent(message: types.Message, bot: Bot):
    user = await crud.get_anonim(
        user_id=message.from_user.id
    )
    if user.status in ('default', 'insearch'): return await message.answer('<i>Вы не находитесь в чатe!</i>')

    await crud.stop_conversation(
        user_id=message.from_user.id,
        partner_id=user.partner_id
    )

    await bot.send_message(
            chat_id=user.partner_id,
            text='<b><i>Собеседник завершил общение.</i></b>',
            reply_markup=anon_menu()
        )

    result = await crud.start_conversation(
        user_id=message.from_user.id
    )
    user = await crud.get_anonim(
        user_id=message.from_user.id
    )

        # начало беседы
    if result:
        await message.answer(
            text=texts.ANONCHAT_START_CONVERSATION,
            reply_markup=registration.remove_kb
            
        )
        await bot.send_message(
            chat_id=user.partner_id,
            text=texts.ANONCHAT_START_CONVERSATION,
            reply_markup=registration.remove_kb
        )

    else:
        await message.answer('<i>Поиск собеседника...</i>\n\n/stop - для прекращения',reply_markup=registration.remove_kb)


@router.message(InConversationFilter())
async def chat(message: types.Message):
    user = await crud.get_anonim(
        user_id=message.from_user.id
    )
    await message.copy_to(
        chat_id=user.partner_id,
        protect_content=True
    )




