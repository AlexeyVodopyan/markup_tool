# thirdparty
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# project
from admin_panel.routes.auth import manager

templates = Jinja2Templates(directory="admin_panel/templates")
base_router = APIRouter()


@base_router.get("/home", response_class=HTMLResponse)
def get_home(request: Request, _=Depends(manager)) -> templates.TemplateResponse:
    return templates.TemplateResponse("new_tasks.html", {"request": request})
