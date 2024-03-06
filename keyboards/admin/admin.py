from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


CANCEL_BTN = InlineKeyboardButton(text='🚫 membatalkan', callback_data="cancel_admin")


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text='📥 masuk', callback_data="notifications"),
        InlineKeyboardButton(text='✏️ langganan', callback_data="subs")
    )
    builder.row(
        InlineKeyboardButton(text='👁 tayangan', callback_data="views"),
        InlineKeyboardButton(text='👋 Salam', callback_data="greetings")
    )
    builder.row(
        InlineKeyboardButton(text='⛓ tautan', callback_data="refs"),
        InlineKeyboardButton(text="👥 semua pengguna", callback_data='CSV')
    )
    builder.row(
        InlineKeyboardButton(text='👥 pengguna langsung', callback_data="csv"),
        InlineKeyboardButton(text='🔄 perbarui file yang valid', callback_data="updateCsv")
    )
    builder.row(
        InlineKeyboardButton(text='📊 statistik', callback_data="stats"),
        InlineKeyboardButton(text='♿️ hapus tidak aktif', callback_data="deleteInactive")
    )
    builder.row(
        CANCEL_BTN
    )

    return builder.as_markup()


def generate_or_cancel_ref():
    builder = InlineKeyboardBuilder()
    builder.button(
        text='🌀 menghasilkan',
        callback_data='gen_ref'
    )
    builder.button(
        text='🚫 membatalkan',
        callback_data='refs'
    )
    builder.adjust(1)
    return builder.as_markup()


def cancel_action(return_to: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='🚫 membatalkan',
        callback_data=return_to
    )
    return builder.as_markup()


def user_stats_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🐵 ringkasan pengguna', callback_data='stats'),
        width=1
    )
    builder.row(
        InlineKeyboardButton(text='🔙 kembali', callback_data="admin"),
        CANCEL_BTN
    )

    return builder.as_markup()


def back_to_menu(with_cancel: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🔙 kembali', callback_data="admin"),
        width=2
    )
    if with_cancel:
        builder.add(CANCEL_BTN)

    return builder.as_markup()


def mandatory_subs_list(subs_list: list):
    builder = InlineKeyboardBuilder()

    for num, sub in enumerate(subs_list, start=1):
        builder.row(InlineKeyboardButton(text=f'{sub.channel_name}', callback_data="manageSub_{}".format(sub.id)))

    builder.row(InlineKeyboardButton(text='🆕 tambah baru', callback_data="createSub"))
    builder.row(InlineKeyboardButton(text='🤖 tambahkan bot baru', callback_data="createSubBot"))
    builder.row(
        InlineKeyboardButton(text='🔙 kembali', callback_data="admin"),
        CANCEL_BTN
    )

    return builder.as_markup()


def delete_sub(sub_id: int):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='❌ hapus op', callback_data="deleteSub_{}".format(sub_id)))
    builder.row(
        InlineKeyboardButton(text='🔙 kembali', callback_data="admin"),
        CANCEL_BTN
    )

    return builder.as_markup()


def current_views_list(views_list: list):
    builder = InlineKeyboardBuilder()

    for view in views_list:
        builder.row(InlineKeyboardButton(text='{}'.format(view.name), callback_data="manageView_{}".format(view.id)))

    builder.row(InlineKeyboardButton(text='🆕 membuat baru', callback_data="CreateView"))
    builder.row(
        InlineKeyboardButton(text='🔙 kembali', callback_data="admin"),
        CANCEL_BTN
    )

    return builder.as_markup()


def view_options(view_id: int):
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='❌ hapus pertunjukan', callback_data="deleteView_{}".format(view_id)))
    builder.row(InlineKeyboardButton(text='👁 lihat pertunjukan', callback_data="watchView_{}".format(view_id)))
    builder.row(
        InlineKeyboardButton(text='🔙 kembali', callback_data="views"),
        CANCEL_BTN
    )

    return builder.as_markup()


def refresh_notifications_status():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="memperbarui", callback_data='refreshNotify'))

    return builder.as_markup()


def where_to_send_notifications_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 pengguna", callback_data="users_notifications"),
        InlineKeyboardButton(text="👥 kelompok", callback_data="chats_notifications")
    )
    builder.row(
        InlineKeyboardButton(text="🌐 di mana pun", callback_data="all_notifications")
    )
    builder.row(
        InlineKeyboardButton(text='🔙 kembali ke menu', callback_data="admin"),
        CANCEL_BTN
    )

    return builder.as_markup()


def refs_menu():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text='🆕 menambahkan', callback_data="createref"),
        InlineKeyboardButton(text="❌ menghapus", callback_data="delrefs")
    )
    builder.row(
        InlineKeyboardButton(text='🔙 kembali', callback_data="admin"),
        CANCEL_BTN
    )

    return builder.as_markup()
