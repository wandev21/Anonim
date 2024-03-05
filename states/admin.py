from aiogram.fsm.state import StatesGroup, State


class PopulateTestsSG(StatesGroup):
    get_file = State()


class Notifs(StatesGroup):
    createref = State()
    createref2 = State()
    sub_get_bot_token = State()
    sub_get_bot_url = State()

    create_sub = State()
    create_sub2 = State()
    first_step = State()
    second_step = State()
    create_view = State()
    create_view2 = State()
    create_view3 = State()


class GreetingsSG(StatesGroup):
    get_new_greeting = State()
