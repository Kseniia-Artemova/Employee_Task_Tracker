from typing import List

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from tortoise.query_utils import Prefetch

from app.employees import services
from app.employees.models import Employee
from app.employees.schemas import PydenticEmployeeOut, PydenticEmployeeCreate, PydenticEmployeePut, \
    PydenticEmployeeOutWithTask
from app.tasks.models import Task
from app.tasks.schemas import PydanticTaskOutForEmployee
from app.users.auth_utils import get_current_user, check_superuser_or_staff
from app.users.models import User

employees_router = APIRouter()


@employees_router.get('/sorted_by_tasks/')
async def get_employees_sorted(current_user: User = Depends(get_current_user)) -> List:  # noqa: F841
    """
    Вывод списка сотрудников и их задач, отсортированный по количеству активных задач

    :param current_user: текущий пользователь
    :return: список сотрудников
    """

    employees = await Employee.filter(taskss__status__not='completed').distinct().prefetch_related(
        Prefetch('taskss', queryset=Task.all()))

    employees_sorted = sorted(employees, key=lambda e: len(e.taskss))

    employees_with_tasks = []

    for employee in employees_sorted:
        employee_new = PydenticEmployeeOutWithTask.model_validate(employee)
        employee_new.tasks = [PydanticTaskOutForEmployee.model_validate(task) for task in employee.taskss]
        employees_with_tasks.append(employee_new)

    return employees_with_tasks


@employees_router.get('/', response_model=List[PydenticEmployeeOut])
async def get_employees(current_user: User = Depends(get_current_user)) -> List[Employee]:  # noqa: F841
    """
    Вывод списка сотрудников

    :param current_user: текущий пользователь
    :return: список сотрудников
    """

    employees = await Employee.all()
    return employees


@employees_router.get('/{employee_id}/', response_model=PydenticEmployeeOut)
async def get_employee(employee_id: int, current_user: User = Depends(get_current_user)) -> Employee:  # noqa: F841
    """
    Вывод информации о сотруднике по идентификатору

    :param employee_id: идентификатор сотрудника
    :param current_user: текущий пользователь
    :return: сотрудник
    """

    employee_obj = await services.get_employee_or_404(employee_id)
    return employee_obj


@employees_router.post('/', response_model=PydenticEmployeeOut)
async def create_employee(employee: PydenticEmployeeCreate,
                          current_user: User = Depends(check_superuser_or_staff)) -> Employee:  # noqa: F841
    """
    Создание нового сотрудника

    :param employee: данные о сотруднике
    :param current_user: текущий пользователь
    :return: созданный сотрудник
    """

    employee_obj = await Employee.create(**employee.model_dump(exclude_unset=True))
    return employee_obj


@employees_router.put('/{employee_id}/', response_model=PydenticEmployeeOut)
async def update_employee(employee_id: int, employee: PydenticEmployeePut,
                          current_user: User = Depends(check_superuser_or_staff)) -> Employee:  # noqa: F841
    """
    Обновление информации о сотруднике

    :param employee_id: идентификатор сотрудника
    :param employee: данные о сотруднике
    :param current_user: текущий пользователь
    :return: обновленный сотрудник
    """

    employee_obj = await services.get_employee_or_404(employee_id)
    employee_update_data = employee.model_dump(exclude_unset=True)
    for key, value in employee_update_data.items():
        setattr(employee_obj, key, value)
    await employee_obj.save()
    return employee_obj


@employees_router.delete('/{employee_id}/')
async def delete_employee(employee_id: int,
                          current_user: User = Depends(check_superuser_or_staff)) -> JSONResponse:  # noqa: F841
    """
    Удаление сотрудника по идентификатору

    :param employee_id: идентификатор сотрудника
    :param current_user: текущий пользователь
    :return: сообщение об успешном удалении
    """

    employee_obj = await services.get_employee_or_404(employee_id)
    await employee_obj.delete()
    content = {'message': f'Сотрудник {employee_id} удалён'}

    return JSONResponse(content=content, status_code=200)
