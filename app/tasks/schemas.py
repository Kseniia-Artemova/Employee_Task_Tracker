from datetime import datetime

from pydantic import BaseModel, field_validator
from app.employees.schemas import EmployeeForTask
from app.employees.validators import ChoiceValidator

choice_validator = ChoiceValidator(choices=('new', 'in_progress', 'completed'))


class PydanticTaskCreate(BaseModel):
    """
    Модель для создания задачи
    """

    name: str
    description: str | None = None
    performer: int | None = None
    deadline: datetime | None = None
    status: str = "new"
    parent_task: int | None = None

    @field_validator('status')
    @classmethod
    def check_status(cls, value: str) -> str:
        """Проверка на допустимый статус задачи"""

        choice_validator(value)
        return value

    class Config:
        from_attributes = True


class PydanticTaskPut(PydanticTaskCreate):
    """
    Модель для обновления задачи
    """

    name: str | None = None
    description: str | None = None
    performer: int | None = None
    deadline: datetime | None = None
    status: str = None
    parent_task: int | None = None


class PydanticParentTaskOut(BaseModel):
    """
    Модель для вывода родительской задачи
    """

    id: int
    name: str
    description: str | None = None
    created_at: datetime
    deadline: datetime | None = None
    status: str
    performer: EmployeeForTask | None = None

    class Config:
        from_attributes = True


class PydanticTaskOut(BaseModel):
    """
    Модель для вывода задачи
    """

    id: int
    name: str
    description: str | None = None
    created_at: datetime
    deadline: datetime | None = None
    status: str
    performer: EmployeeForTask | None = None
    parent_task: PydanticParentTaskOut | None = None

    class Config:
        from_attributes = True


class PydanticTaskOutForEmployee(BaseModel):
    """
    Модель для вывода задачи для связанного с ней сотрудника
    """

    id: int
    name: str
    description: str | None = None
    deadline: datetime | None = None
    status: str

    class Config:
        from_attributes = True
