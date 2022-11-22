# thirdparty
from aiogram.dispatcher.filters.state import State, StatesGroup


class UserFlow(StatesGroup):
    waiting_for_signin = State()
    waiting_for_menu = State()
    waiting_for_tasks = State()
    waiting_for_concrete_task = State()
