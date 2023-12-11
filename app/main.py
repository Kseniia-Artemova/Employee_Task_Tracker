from fastapi import FastAPI

from tortoise.contrib.fastapi import register_tortoise

from app.employees.routers import employees_router
from app.tasks.routers import tasks_router
from app.users.routers import users_router
from app_config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

TORTOISE_ORM = {
    "connections": {
        "default":
            f"postgres://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    },
    "apps": {
        "employees": {
            "models": ["app.employees.models", "aerich.models"],
            "default_connection": "default",
        },
        "tasks": {
            "models": ["app.tasks.models", "aerich.models"],
            "default_connection": "default",
        },
        "users": {
            "models": ["app.users.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

app = FastAPI()
app.include_router(users_router, prefix='/users', tags=['users'])
app.include_router(employees_router, prefix='/employees', tags=['employees'])
app.include_router(tasks_router, prefix='/tasks', tags=['tasks'])

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)