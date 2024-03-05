from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def unsubbed(follows: dict):
    kb = InlineKeyboardBuilder()
    cnt = 0
    btn = []

    for channel in follows['subs']:
        cnt += 1
        btn.append(InlineKeyboardButton(text=f"Канал #{cnt}", url=channel.url))

    kb.row(*btn, width=2)
    kb.row(
        InlineKeyboardButton(text="✅ Продолжить", callback_data="continue")
    )

    return kb.as_markup()
