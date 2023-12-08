from typing import List

from starlette import status
from tortoise.exceptions import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from app.employees import services
from app.employees.models import Employee
from app.employees.schemas import PydenticEmployeeOut, PydenticEmployeeIn
from app.users.auth import get_current_user, check_superuser_or_staff
from app.users.models import User

employees_router = APIRouter()


@employees_router.get('/', response_model=List[PydenticEmployeeOut])
async def get_employees(current_user: User = Depends(get_current_user)):
    employees = await Employee.all()
    return [PydenticEmployeeOut.model_validate(employee) for employee in employees]


@employees_router.get('/{employee_id}/', response_model=PydenticEmployeeOut)
async def get_employee(employee_id: int, current_user: User = Depends(get_current_user)):
    employee_obj = await services.get_employee_or_404(employee_id)
    return PydenticEmployeeOut.model_validate(employee_obj)


@employees_router.post('/', response_model=PydenticEmployeeOut)
async def create_employee(employee: PydenticEmployeeIn, current_user: User = Depends(check_superuser_or_staff)):
    try:
        employee_obj = await Employee.create(**employee.model_dump(exclude_unset=True))
        return PydenticEmployeeOut.model_validate(employee_obj)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {exc}"
        )


@employees_router.put('/{employee_id}/', response_model=PydenticEmployeeOut)
async def update_employee(employee_id: int, employee: PydenticEmployeeIn,
                          current_user: User = Depends(check_superuser_or_staff)):
    try:
        employee_obj = await services.get_employee_or_404(employee_id)
        employee_update_data = employee.model_dump(exclude_unset=True)
        for key, value in employee_update_data.items():
            setattr(employee_obj, key, value)
        await employee_obj.save()
        return PydenticEmployeeOut.model_validate(employee_obj)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {exc}"
        )


@employees_router.delete('/{employee_id}/')
async def delete_employee(employee_id: int, current_user: User = Depends(check_superuser_or_staff)):
    employee_obj = await services.get_employee_or_404(employee_id)
    await employee_obj.delete()
    content = {'message': f'Сотрудник {employee_id} удалён'}

    return JSONResponse(content=content, status_code=200)