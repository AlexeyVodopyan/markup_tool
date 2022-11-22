# stdlib
from typing import TypedDict

# thirdparty
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# project
from common.models import Image, LabelClass, LabeledImage, Task, TaskLabelClass, WebUser


class Statistics(TypedDict):
    total_objects: int
    labeled_objects: int
    classes: list[dict[str, int]]
    tasks: int
    tg_users: int


async def _check_labels(session: AsyncSession, labels: list[str]) -> list[str]:
    """Удаление дубликатов из лейблов"""

    query = select(LabelClass.name).filter(LabelClass.name.in_(labels))
    result = await session.execute(query)
    result = {name[0] for name in result.all()}

    return list(set(labels) - result)


async def save_task(session: AsyncSession) -> int:
    """Сохранение задачи в базу"""

    task = Task()
    session.add(task)
    await session.commit()

    task_query = select(Task.id).order_by(Task.created_at.desc()).limit(1)
    task_id = await session.execute(task_query)

    return task_id.scalar()


async def save_labels(session: AsyncSession, labels: list[str]) -> list[int]:
    """Сохранение классов в базу"""

    new_labels = await _check_labels(session, labels)
    label_classes = [LabelClass(name=label) for label in new_labels]

    if label_classes:
        session.add_all(label_classes)
        await session.commit()

    id_query = select(LabelClass.id).filter(LabelClass.name.in_(labels))
    result = await session.execute(id_query)

    label_ids = [label_id[0] for label_id in result.all()]

    return label_ids


async def save_task_labels(
    session: AsyncSession, task_id: int, labels_id: list[int]
) -> None:
    """Сохранение привязки классов к задаче в базу"""

    task_labels = [
        TaskLabelClass(task_id=task_id, label_class_id=label_id)
        for label_id in labels_id
    ]
    session.add_all(task_labels)
    await session.commit()


async def save_image_fps(
    session: AsyncSession, task_id: int, image_fps: list[str]
) -> None:
    """Сохранение путей к файлам в базу"""

    images = [Image(task_id=task_id, file_path=fp) for fp in image_fps]
    session.add_all(images)
    await session.commit()


async def get_current_user_by_login(session: AsyncSession, username: str) -> str | None:
    """Проверка логина в БД"""
    query = select(WebUser.login).filter_by(
        login=username,
    )
    result = await session.execute(query)

    return result.scalar()


async def check_user_from_db(
    session: AsyncSession, username: str, password: str
) -> bool:
    """Проверка логина и пароля в БД"""
    query = select(WebUser.login).filter_by(login=username, password=password)
    result = await session.execute(query)

    return result.one_or_none() is not None


async def get_statistics(
    session: AsyncSession,
) -> Statistics:
    total_obj_query = select([func.count(Image.id)])
    labeled_objects_query = select([func.count(LabeledImage.image_id.distinct())])
    # classes =

    total_objects = await session.execute(total_obj_query)
    labeled_objects = await session.execute(labeled_objects_query)

    result: Statistics = {
        "total_objects": total_objects.scalar(),
        "labeled_objects": labeled_objects.scalar(),
    }

    return result
