from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.functions import Count

from app.employees.models import Employee
from app.employees.schemas import EmployeeForTask
from app.tasks.models import Task


async def get_task_or_404(task_id: int) -> Task:
    """
    Получение задачи по идентификатору или исключение, если не найдена

    :param task_id: идентификатор задачи
    :return: задача или исключение
    """

    task_obj = await Task.get_or_none(id=task_id).prefetch_related('performer',
                                                                   'parent_task',
                                                                   'parent_task__performer')
    if task_obj is None:
        raise HTTPException(status_code=404, detail=f'Задача {task_id} не найдена')
    return task_obj


async def get_least_busy_employees() -> tuple[list[EmployeeForTask], int]:
    """
    Получение минимального количества задач у сотрудников и списка сотрудников с этим количеством задач

    :return: кортеж, состоящий из списка сотрудников и минимального количества задач
    """
    employee_task_counts = await Employee.annotate(
        unfinished_task_count=Count('taskss', _filter=Q(taskss__status__not='completed'))
    ).values('id', 'unfinished_task_count')

    if not employee_task_counts:
        return [], 0

    min_task_count = min(emp['unfinished_task_count'] or 0 for emp in employee_task_counts)

    least_loaded_employee_ids = [emp['id'] for emp in employee_task_counts
                                 if emp['unfinished_task_count'] == min_task_count]

    least_loaded_employees = await Employee.filter(id__in=least_loaded_employee_ids).all()

    return [EmployeeForTask.model_validate(emp) for emp in least_loaded_employees], min_task_count


async def get_free_employees() -> list[EmployeeForTask]:
    """
    Получение списка полностью свободных сотрудников

    :return: список свободных сотрудников
    """
    employees = await Employee.annotate(
        task_count=Count('taskss'),
        completed_task_count=Count('taskss', _filter=Q(taskss__status='completed'))
    )
    return [EmployeeForTask.model_validate(emp) for emp in employees
            if emp.task_count == 0 or emp.task_count == emp.completed_task_count]


async def get_available_employee(task: Task, min_task_count: int) -> EmployeeForTask | None:
    """
    Получение доступного сотрудника для задачи
    Здесь мы сравниваем количество задач у сотрудника,
    выполняющего родительскую задачу с минимальным количеством задач.
    Если у сотрудника, выполняющего родительскую задачу на две или меньше задач меньше,
    чем минимальное по списку сотрудников, то мы возвращаем его. Иначе - None

    :param task: объект задачи
    :param min_task_count: минимальное количество задач
    :return: объект сотрудника или None
    """

    if task.parent_task_id and task.parent_task and task.parent_task.performer_id:
        performer = await Employee.get(id=task.parent_task.performer_id)
        performer_task_count = await Task.filter(
            performer=performer,
            status__not='completed'
        ).count()

        if performer_task_count - min_task_count <= 2:
            return EmployeeForTask.model_validate(performer)

    return None