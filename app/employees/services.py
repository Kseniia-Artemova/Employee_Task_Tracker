from fastapi import HTTPException

from app.employees.models import Employee


async def get_employee_or_404(employee_id: int) -> Employee:
    """
    Получение сотрудника по идентификатору или исключение, если не найден

    :param employee_id: идентификатор сотрудника
    :return: сотрудник или исключение
    """

    employee_obj = await Employee.get_or_none(id=employee_id)
    if employee_obj is None:
        raise HTTPException(status_code=404, detail=f'Сотрудник {employee_id} не найден')
    return employee_obj