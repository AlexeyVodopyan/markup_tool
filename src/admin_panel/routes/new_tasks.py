# thirdparty
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

# project
from admin_panel.routes.auth import manager
from admin_panel.service.files_download import download_images
from admin_panel.service.queries import (
    save_image_fps,
    save_labels,
    save_task,
    save_task_labels,
)
from common.db_settings import get_session

new_task_router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="admin_panel/templates")
ACCEPTED_EXTENSIONS = {"image/png", "image/jpeg"}


def validate_request(labels: list[str], images: list[UploadFile]) -> None:
    """Валидация данных запроса"""
    if len(labels) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Количество классов < 2, увеличьте число классов",
        )
    for file in images:
        if file.content_type not in ACCEPTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Некорректный формат файла {file.filename}: {file.content_type}",
            )


@new_task_router.post(
    "/home", status_code=status.HTTP_201_CREATED, response_class=HTMLResponse
)
async def save_new_tasks(
    request: Request,
    images: list[UploadFile] = File(),
    labels: str = Form(),
    session: AsyncSession = Depends(get_session),
    _=Depends(manager),
) -> templates.TemplateResponse:
    """Отправка новой задачи на разметку"""

    labels = list(set(labels.split()))

    validate_request(labels, images)

    image_fps = download_images(images)

    task_id = await save_task(session)
    labels_id = await save_labels(session, labels)
    await save_task_labels(session, task_id, labels_id)
    await save_image_fps(session, task_id, image_fps)

    return templates.TemplateResponse("new_tasks.html", {"request": request})
