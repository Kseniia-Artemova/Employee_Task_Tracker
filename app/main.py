from fastapi import FastAPI
from pydantic import ValidationError as PydanticValidationError
from starlette.responses import JSONResponse

from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import ValidationError as TortoiseValidationError

from app.employees.routers import employees_router
from app.tasks.routers import tasks_router
from app.users.routers import users_router
from app.config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    },
    "apps": {
        "employees": {
            "models": ["app.employees.models"],
            "default_connection": "default",
        },
        "tasks": {
            "models": ["app.tasks.models", "aerich.models"],
            "default_connection": "default",
        },
        "users": {
            "models": ["app.users.models"],
            "default_connection": "default",
        },
    },
}

# TORTOISE_ORM = {
#     "connections": {
#         "default":
#             f"postgres://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#     },
#     "apps": {
#         "models": {
#             "models": ["app.users.models", "app.tasks.models", "app.employees.models"],
#             "default_connection": "default",
#         },
#     },
# }

app = FastAPI()
app.include_router(users_router, prefix='/users', tags=['users'])
app.include_router(employees_router, prefix='/employees', tags=['employees'])
app.include_router(tasks_router, prefix='/tasks', tags=['tasks'])


@app.exception_handler(TortoiseValidationError)
async def tortoise_validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


# @app.exception_handler(PydanticValidationError)
# async def pydantic_validation_exception_handler(request, exc):
#     errors = [{"loc": e["loc"], "msg": e["msg"]} for e in exc.errors()]
#     return JSONResponse(
#         status_code=400,
#         content={"detail": errors},
#     )


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)