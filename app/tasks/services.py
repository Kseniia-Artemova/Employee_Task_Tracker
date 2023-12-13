from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.functions import Count

from app.employees.models import Employee
from app.employees.schemas import EmployeeForTask
from app.tasks.models import Task


async def get_task_or_404(task_id: int) -> Task:
    task_obj = await Task.get_or_none(id=task_id).prefetch_related('performer',
                                                                   'parent_task',
                                                                   'parent_task__performer')
    if task_obj is None:
        raise HTTPException(status_code=404, detail=f'Задача {task_id} не найдена')
    return task_obj


async def get_least_loaded_employee():
    return await Employee.annotate(
        task_count=Count('taskss', _filter=Q(taskss__status__not='completed'))
    ).order_by('task_count').first()


async def get_free_employees():
    employees = await Employee.annotate(
        task_count=Count('taskss'),
        completed_task_count=Count('taskss', _filter=Q(taskss__status='completed'))
    )
    return [EmployeeForTask.from_orm(emp) for emp in employees
            if emp.task_count == 0 or emp.task_count == emp.completed_task_count]


async def get_available_employee(task, least_busy_employee):
    if task.parent_task_id and task.parent_task and task.parent_task.performer_id:
        performer = await Employee.get(id=task.parent_task.performer_id)
        performer_task_count = await Task.filter(
            performer=performer,
            status__not='completed'
        ).count()

        if performer_task_count - least_busy_employee.task_count <= 2:
            return EmployeeForTask.from_orm(performer)

    return EmployeeForTask.from_orm(least_busy_employee) if least_busy_employee else None