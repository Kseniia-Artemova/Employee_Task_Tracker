from datetime import datetime
from pydantic import BaseModel, field_validator
from app.employees.schemas import EmployeeForTask
from app.employees.validators import ChoiceValidator

choice_validator = ChoiceValidator(choices=('new', 'in_progress', 'completed'))


class PydanticTaskIn(BaseModel):
    name: str
    description: str | None = None
    performer: int | None = None
    deadline: datetime | None = None
    status: str = "new"
    parent_task: int | None = None

    @field_validator('status')
    @classmethod
    def check_status(cls, value: str) -> str:
        choice_validator(value)
        return value

    class Config:
        from_attributes = True


class PydanticParentTaskOut(BaseModel):
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


