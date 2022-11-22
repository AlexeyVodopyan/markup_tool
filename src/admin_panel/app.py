# thirdparty
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# project
from admin_panel.routes.auth import auth_router
from admin_panel.routes.base import base_router
from admin_panel.routes.new_tasks import new_task_router

app = FastAPI()

app.include_router(base_router)
app.include_router(new_task_router)
app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("admin_panel.app:app", reload=True)
