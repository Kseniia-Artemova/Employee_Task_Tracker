from datetime import datetime

from pydantic import BaseModel, EmailStr, model_validator

from app.employees.models import only_digits_validator


class BaseEmployeeOut(BaseModel):

    @model_validator(mode='before')
    def calculate_full_name(self):
        first_name = self.first_name
        last_name = self.last_name
        father_name = self.father_name
        if first_name and last_name:
            parts = [last_name, first_name]
            if father_name:
                parts.append(father_name)
            self.full_name = ' '.join(parts)
        return self


class PydenticEmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    father_name: str | None = None
    email: EmailStr
    phone: str
    address: str | None = None
    position: str | None = None

    class Config:
        from_attributes = True
        validators = {
            'phone': [only_digits_validator]
        }


class PydenticEmployeePut(BaseModel):
    first_name: str = None
    last_name: str = None
    father_name: str | None = None
    email: EmailStr = None
    phone: str = None
    address: str | None = None
    position: str | None = None

    class Config:
        from_attributes = True
        validators = {
            'phone': [only_digits_validator]
        }


class PydenticEmployeeOut(BaseEmployeeOut):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    address: str | None = None
    position: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
        validators = {
            'phone': [only_digits_validator]
        }


class EmployeeForTask(BaseEmployeeOut):
    full_name: str
