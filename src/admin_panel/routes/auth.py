# stdlib
import os

# thirdparty
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from service.queries import check_user_from_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# project
from common.db_settings import Session, get_session
from common.models import WebUser

templates = Jinja2Templates(directory="templates")
auth_router = APIRouter()

manager = LoginManager(os.environ.get("SECRET"), token_url="/login", use_cookie=True)


@manager.user_loader()
async def get_current_user_by_login(
    username: str, session: AsyncSession = None
) -> str | None:
    """Проверка логина в БД"""

    query = select(WebUser.login).filter_by(
        login=username,
    )

    if session is None:
        async with Session() as session:
            result = await session.execute(query)
            return result.scalar()

    result = await session.execute(query)

    return result.scalar()


@auth_router.get("/", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@auth_router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user_true = await check_user_from_db(
        session, form_data.username, form_data.password
    )

    if not user_true:
        return InvalidCredentialsException

    access_token = manager.create_access_token(data={"sub": form_data.username})
    resp = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp, access_token)
    return resp


@auth_router.get("/logout", response_class=HTMLResponse)
def logout(__: Request, _=Depends(manager)):
    resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp, "")
    return resp
