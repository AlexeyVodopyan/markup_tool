# thirdparty
from aiogram import types
from aiogram.dispatcher import FSMContext

# project
from telegram_bot.service.queries import (
    add_new_tasks,
    add_new_user,
    check_login_pass,
    get_active_user_tasks,
)
from telegram_bot.state.state import UserFlow


async def start(message: types.Message, state: FSMContext) -> None:
    """Отправляет приветственное сообщение и вызывает стартовое меню"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    markup.add("Зарегистрироваться", "Войти", "Выйти")

    await message.answer(
        "Бот для разметки изображений\n\n"
        "Для начала работы необходимо "
        "зарегистрироваться и авторизоваться в профиле.\n"
        "Используйте кнопки для навигации",
        reply_markup=markup,
    )

    await state.set_state(UserFlow.waiting_for_signin)


async def sign_up(message: types.Message, state: FSMContext) -> None:
    """
    Регистрация нового пользователя
    """

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Войти", "Выйти")

    db_session = message.bot.get("db")
    async with db_session() as session:
        login, password = await add_new_user(session)

    await message.reply(
        f"Ваш логин: `{login}`\n"
        f"Ваш пароль: `{password}`\n"
        "Используйте их для входа\. \n"  # noqa
        "Для того чтобы авторизоваться нажмите кнопку 'Войти'",
        reply_markup=markup,
        parse_mode="MarkDownV2",
    )

    await state.set_state(UserFlow.waiting_for_signin)


async def sign_in(message: types.Message, state: FSMContext) -> None:
    """
    Авторизация пользователя
    """

    await message.reply(
        "Введите логин и пароль, разделенные пробелом \n" "Например: pasha 123456",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    await state.set_state(UserFlow.waiting_for_menu)


async def get_menu(message: types.Message, state: FSMContext) -> None:
    """Внутреннее меню пользователя после авторизации"""

    try:
        login, password = message.text.split(" ")
    except ValueError:
        await message.reply(
            "Неправильный формат ввода логина и пароля. \n" "Попробуйте еще раз"
        )
        return

    db_session = message.bot.get("db")

    async with db_session() as session:
        check_user = await check_login_pass(session, login, password)

        if not check_user:
            await message.reply(
                "Неправильный логин или пароль. \n" "Попробуйте еще раз"
            )
            return

    await state.update_data(login=login)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    markup.add("Мои задачи", "Выйти")

    await message.reply(
        "Вы успешно авторизовались. \n" "Для перехода к разметке нажмите Мои задачи",
        reply_markup=markup,
    )

    await state.set_state(UserFlow.waiting_for_tasks)


async def get_tasks(message: types.Message, state: FSMContext) -> None:
    """Получение списка назначенных задач"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    db_session = message.bot.get("db")

    async with db_session() as session:
        # Присвоим новые задачи пользователю
        user_data = await state.get_data()
        await add_new_tasks(session, user_data["login"])
        tasks = await get_active_user_tasks(session, user_data["login"])

    tasks.extend(["Обновить", "Выйти"])
    markup.add(*tasks)

    await message.reply("Выберите задачу для выполнения", reply_markup=markup)

    await state.set_state(UserFlow.waiting_for_concrete_task)


async def go_exit(message: types.Message, state: FSMContext) -> None:
    """Действие при нажатии кнопки выйти"""
    await state.finish()

    await message.reply(
        "Вы вышли из бота. \n" "Для повторной работы воспользуйтесь командой /start",
        reply_markup=types.ReplyKeyboardRemove(),
    )
