from aiogram.utils.keyboard import InlineKeyboardBuilder, CallbackData


class DeleteTestCD(CallbackData, prefix='delete_test'):
    test_id: int


def delete_test_menu(test_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Удалить',
        callback_data=DeleteTestCD(test_id=test_id)
    )
    return builder.as_markup()
