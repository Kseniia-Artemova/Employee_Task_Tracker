from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.employees.models import Employee
from app.tasks import services
from app.tasks.models import Task
from app.tasks.schemas import PydanticTaskOut, PydanticTaskIn
from app.users.auth import get_current_user, check_superuser_or_staff
from app.users.models import User

tasks_router = APIRouter()


@tasks_router.get('/', response_model=List[PydanticTaskOut])
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = await Task.all()
    return [PydanticTaskOut.model_validate(task) for task in tasks]


@tasks_router.get('/{task_id}/', response_model=PydanticTaskOut)
async def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    task_obj = await services.get_task_or_404(task_id)
    return PydanticTaskOut.model_validate(task_obj)


@tasks_router.post('/', response_model=PydanticTaskOut)
async def create_task(task: PydanticTaskIn, current_user: User = Depends(check_superuser_or_staff)):
    try:
        performer = await Employee.get(id=task.performer) if task.performer else None
        parent_task = await Task.get(id=task.parent_task) if task.parent_task else None

        task_obj = await Task.create(
            name=task.name,
            description=task.description,
            performer=performer,
            deadline=task.deadline,
            status=task.status,
            parent_task=parent_task
        )
        return PydanticTaskOut.model_validate(task_obj)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {exc}",
        )


@tasks_router.put('/{task_id}/', response_model=PydanticTaskOut)
async def update_task(task_id: int, task: PydanticTaskIn, current_user: User = Depends(check_superuser_or_staff)):
    try:
        task_obj = await services.get_task_or_404(task_id)
        task_update_data = task.model_dump(exclude_unset=True)
        for key, value in task_update_data.items():
            setattr(task_obj, key, value)
        await task_obj.save()
        return PydanticTaskOut.model_validate(task_obj)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {exc}",
        )


@tasks_router.delete('/{task_id}/')
async def delete_task(task_id: int, current_user: User = Depends(check_superuser_or_staff)):
    task_obj = await services.get_task_or_404(task_id)
    await task_obj.delete()
    content = {'message': f'Задача {task_id} удалена'}

    return JSONResponse(content=content, status_code=200)