# thirdparty
from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, Text

# project
from telegram_bot.handlers.image_processing import process_image
from telegram_bot.handlers.user_flow import (
    get_menu,
    get_tasks,
    go_exit,
    sign_in,
    sign_up,
    start,
)
from telegram_bot.state.state import UserFlow


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков команд бота"""
    dp.register_message_handler(start, CommandStart(), state="*")
    dp.register_message_handler(
        sign_up,
        Text(equals="зарегистрироваться", ignore_case=True),
        state=UserFlow.waiting_for_signin,
    )
    dp.register_message_handler(
        sign_in,
        Text(equals="войти", ignore_case=True),
        state=UserFlow.waiting_for_signin,
    )
    dp.register_message_handler(get_menu, state=UserFlow.waiting_for_menu)
    dp.register_message_handler(
        get_tasks,
        Text(equals=["мои задачи", "обновить"], ignore_case=True),
        state=[UserFlow.waiting_for_tasks, UserFlow.waiting_for_concrete_task],
    )
    dp.register_message_handler(
        go_exit, Text(equals="выйти", ignore_case=True), state="*"
    )
    dp.register_message_handler(process_image, state=UserFlow.waiting_for_concrete_task)
