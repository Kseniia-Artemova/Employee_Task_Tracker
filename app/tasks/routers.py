from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from app.employees.models import Employee
from app.tasks import services
from app.tasks.models import Task
from app.tasks.schemas import PydanticTaskOut, PydanticTaskCreate, PydanticTaskPut
from app.users.auth_utils import get_current_user, check_superuser_or_staff
from app.users.models import User

tasks_router = APIRouter()


@tasks_router.get('/important/')
async def get_important_tasks(current_user: User = Depends(get_current_user)):
    tasks = await Task.filter(
        status__not='completed',
        parent_task_id__isnull=False,
        performer_id__isnull=True,
        parent_task__performer_id__isnull=False
    ).prefetch_related('performer', 'parent_task')

    free_employees = await services.get_free_employees()
    important_tasks = []

    if free_employees:
        for task in tasks:
            important_tasks.append({
                "id": task.id,
                "name": task.name,
                "deadline": task.deadline,
                "parent_task": task.parent_task_id,
                "status": task.status,
                "available_employees": free_employees
            })
    else:
        least_loaded_employee = await services.get_least_loaded_employee()
        for task in tasks:
            available_employee = await services.get_available_employee(task, least_loaded_employee)
            important_tasks.append({
                "id": task.id,
                "name": task.name,
                "deadline": task.deadline,
                "parent_task": task.parent_task_id,
                "status": task.status,
                "available_employee": available_employee
            })

    return important_tasks


@tasks_router.get('/', response_model=List[PydanticTaskOut])
async def get_tasks(current_user: User = Depends(get_current_user)):
    tasks = await Task.all().prefetch_related('performer',
                                              'parent_task',
                                              'parent_task__performer')
    return tasks


@tasks_router.get('/{task_id}/', response_model=PydanticTaskOut)
async def get_task(task_id: int, current_user: User = Depends(get_current_user)):  # noqa: F841
    task_obj = await services.get_task_or_404(task_id)
    return task_obj


@tasks_router.post('/', response_model=PydanticTaskOut)
async def create_task(task: PydanticTaskCreate, current_user: User = Depends(check_superuser_or_staff)):  # noqa: F841
    performer = await Employee.get(id=task.performer) if task.performer else None
    parent_task = await Task.get(id=task.parent_task).prefetch_related('performer') if task.parent_task else None

    task_obj = await Task.create(
        name=task.name,
        description=task.description,
        performer=performer,
        deadline=task.deadline,
        status=task.status,
        parent_task=parent_task
    )
    return task_obj


@tasks_router.put('/{task_id}/', response_model=PydanticTaskOut)
async def update_task(task_id: int, task: PydanticTaskPut, current_user: User = Depends(check_superuser_or_staff)):
    task_obj = await services.get_task_or_404(task_id)

    task_data = task.model_dump(exclude_unset=True)

    if 'performer' in task_data:
        task_obj.performer = await Employee.get(id=task.performer) if task.performer else None

    if 'parent_task' in task_data:
        if task.parent_task == task_id:
            raise HTTPException(status_code=400, detail="Нельзя указывать в качестве родительской задачи саму себя")
        task_obj.parent_task = await Task.get(id=task.parent_task).prefetch_related(
            'performer') if task.parent_task else None

    for key, value in task_data.items():
        if key not in ['performer', 'parent_task']:
            setattr(task_obj, key, value)

    await task_obj.save()
    return task_obj


@tasks_router.delete('/{task_id}/')
async def delete_task(task_id: int, current_user: User = Depends(check_superuser_or_staff)):
    task_obj = await services.get_task_or_404(task_id)
    await task_obj.delete()
    content = {'message': f'Задача {task_id} удалена'}

    return JSONResponse(content=content, status_code=200)