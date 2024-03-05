from aiogram.fsm.state import StatesGroup, State


class CreateTestSG(StatesGroup):
    get_name = State()
    get_template = State()
    get_answers = State()


class EditTestSG(StatesGroup):
    get_answers = State()
    get_cover = State()


class ConfirmTestDeleteSG(StatesGroup):
    confirmation = State()

class Registration(StatesGroup):
    # возраст при регистрации:
    select_age = State()
    # изменение возраста:
    change_age = State()

class Conversation(StatesGroup):
    chat = State()

class AnonTest(StatesGroup):
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()
    question_5 = State()
    question_6 = State()
    question_7 = State()
    question_8 = State()
    question_9 = State()