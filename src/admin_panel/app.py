# thirdparty
import uvicorn
from fastapi import FastAPI

# project
from admin_panel.routes.auth import auth_router
from admin_panel.routes.base import base_router
from admin_panel.routes.new_tasks import new_task_router
from admin_panel.routes.statistics import stat_router

app = FastAPI()

app.include_router(base_router)
app.include_router(new_task_router)
app.include_router(auth_router)
app.include_router(stat_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
