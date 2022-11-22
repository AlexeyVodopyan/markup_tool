# thirdparty
from sqlalchemy import and_, select, update
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession

# project
from common.models import (
    Image,
    LabelClass,
    LabeledImage,
    Task,
    TaskLabelClass,
    TaskStatus,
    TaskTgUser,
    TgUser,
)
from common.utils import generate_random_string


async def add_new_user(session: AsyncSession) -> tuple[str, str]:
    """Добавление нового пользователя в базу"""
    login = generate_random_string()
    password = generate_random_string()

    user = TgUser(login=login, password=password)

    session.add(user)
    await session.commit()

    return login, password


async def check_login_pass(session: AsyncSession, login: str, password: str) -> bool:
    """Проверка логина и пароля"""

    query = select(TgUser).filter_by(login=login, password=password)
    result = await session.execute(query)

    return result.one_or_none() is not None


async def get_active_user_tasks(session: AsyncSession, login: str) -> list[str] | None:
    """Список активных задач пользователя"""

    query = (
        select(Task.id)
        .join(TaskTgUser, TaskTgUser.task_id == Task.id)
        .join(TgUser, TaskTgUser.tg_login == TgUser.login)
        .filter(
            and_(TaskTgUser.status == TaskStatus.ASSIGNED.value, TgUser.login == login)
        )
    )

    result = await session.execute(query)

    result = result.all()

    if result:
        result = [str(res[0]) for res in result]

    return result


async def get_all_image_fps_by_task(
    session: AsyncSession, task_id: int, login: str
) -> list[Row[int, str]] | None:
    """Получение всех неразмеченных id и путей к файлам для выбранной задачи"""

    labeled_image_ids = select(LabeledImage.image_id).filter(
        LabeledImage.tg_login == login
    )

    image_ids = select(
        Image.id,
        Image.file_path,
    ).filter(Image.task_id == task_id, Image.id.not_in(labeled_image_ids))

    result = await session.execute(image_ids)
    return result.all()


async def get_labels_by_task(
    session: AsyncSession, task_id: int
) -> dict[str, int] | None:
    """Получение пути к неразмеченной картинке"""

    labels_query = (
        select(LabelClass.id, LabelClass.name)
        .join(TaskLabelClass, LabelClass.id == TaskLabelClass.label_class_id)
        .filter(TaskLabelClass.task_id == task_id)
    )

    result = await session.execute(labels_query)

    if result:
        result = {label[1]: label[0] for label in result}

    return result


async def add_labeled_image(
    session: AsyncSession, image_id: int, tg_login: str, label_id: int
) -> None:
    """Добавление результата разметки в БД"""
    image = LabeledImage(image_id=image_id, tg_login=tg_login, label_id=label_id)
    session.add(image)
    await session.commit()


async def update_task_status(
    session: AsyncSession, tg_login: str, task_id: int
) -> None:
    """Изменение статуса задачи на Resolved"""
    query = (
        update(TaskTgUser)
        .filter(TaskTgUser.tg_login == tg_login, TaskTgUser.task_id == task_id)
        .values(status=TaskStatus.RESOLVED)
    )
    await session.execute(query)
    await session.commit()


async def add_new_tasks(session: AsyncSession, tg_login: str) -> None:
    """Назначение списка задач свежезарегистрированному пользователю"""
    subq = select(TaskTgUser.task_id).filter(TaskTgUser.tg_login == tg_login).subquery()

    task_query = (
        select(Task.id)
        .join(subq, Task.id == subq.c.task_id, isouter=True)
        .filter(subq.c.task_id.is_(None))
    )
    task_ids = await session.execute(task_query)

    tasks = [
        TaskTgUser(tg_login=tg_login, task_id=task_id[0], status=TaskStatus.ASSIGNED)
        for task_id in task_ids.all()
    ]

    session.add_all(tasks)

    await session.commit()
