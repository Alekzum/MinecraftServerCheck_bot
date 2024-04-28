from aiogram.fsm.state import StatesGroup, State


class Setup(StatesGroup):
    host = State()
    port = State()