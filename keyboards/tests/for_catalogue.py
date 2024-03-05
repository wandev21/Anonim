from aiogram.utils.keyboard import InlineKeyboardBuilder


def catalogue_menu(categories: list[str]):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat, switch_inline_query_current_chat=cat)
    builder.adjust(2)
    return builder.as_markup()
