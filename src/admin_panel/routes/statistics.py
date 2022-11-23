# thirdparty
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

# project
from admin_panel.routes.auth import manager
from admin_panel.service.queries import get_statistics
from common.db_settings import get_session

templates = Jinja2Templates(directory="admin_panel/templates")
stat_router = APIRouter()


@stat_router.get("/statistics")
async def statistics(
    request: Request, _=Depends(manager), session: AsyncSession = Depends(get_session)
):
    result = await get_statistics(session)
    return templates.TemplateResponse(
        "statistics.html", {"stat": result, "request": request}
    )
