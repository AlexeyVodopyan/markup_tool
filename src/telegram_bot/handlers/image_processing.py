# thirdparty
from aiogram import types
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

# project
from telegram_bot.service.queries import (
    add_labeled_image,
    get_all_image_fps_by_task,
    get_labels_by_task,
    update_task_status,
)
from telegram_bot.state.state import UserFlow


async def _finish_task(
    session: AsyncSession, message: types.Message, state: FSMContext, user_data: dict
) -> None:
    """Логика завершения выполнения задачи"""
    await update_task_status(session, user_data["login"], user_data["task_id"])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)

    markup.add("Мои задачи", "Выйти")

    await message.answer(
        text="Задача успешно выполнена. \n"
        "Для перехода к следующим задачам нажмите Мои задачи",
        reply_markup=markup,
    )
    await state.set_state(UserFlow.waiting_for_tasks)
    await state.reset_data()
    await state.update_data(login=user_data["login"])


async def process_image(message: types.Message, state: FSMContext) -> None:
    """Разметка изображений для конкретной задачи"""
    user_data = await state.get_data()

    if "task" not in user_data:
        task_id = int(message.text)
        await state.update_data(task=task_id)
    else:
        task_id = int(user_data["task"])

        label = message.text
        previous_image = user_data["current_image"]
        db_session = message.bot.get("db")

        async with db_session() as session:
            await add_labeled_image(
                session,
                user_data["images"][previous_image][0],
                user_data["login"],
                user_data["labels"][label],
            )

            if previous_image == len(user_data["images"]) - 1:
                await _finish_task(session, message, state, user_data)
                return

            await state.update_data(current_image=previous_image + 1)
            user_data = await state.get_data()

    if "images" in user_data and "labels" in user_data:
        # TODO: Сделать проверку и загрузку из Redis
        image = user_data["images"][user_data["current_image"]]
        labels = user_data["labels"]
    else:
        db_session = message.bot.get("db")

        async with db_session() as session:
            images = await get_all_image_fps_by_task(
                session, task_id, user_data["login"]
            )
            labels = await get_labels_by_task(session, task_id)

            current_image = 0

        image = images[current_image]

        # TODO: Сделать сохранение состояния в Redis
        await state.update_data(
            task_id=task_id, current_image=current_image, images=images, labels=labels
        )

    media = types.MediaGroup()
    media.attach_photo(types.InputFile(image[1]))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(*[label for label in labels])
    await message.answer_media_group(media=media)
    await message.answer(text="Выберите класс картинки", reply_markup=markup)
