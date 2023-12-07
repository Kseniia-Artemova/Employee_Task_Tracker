from datetime import datetime

from pydantic import BaseModel, EmailStr, constr


class PydenticUserRegister(BaseModel):
    """Модель пользователя для получения данных"""

    email: EmailStr
    password: constr(max_length=255)
    first_name: str | None = None
    last_name: str | None = None


class PydenticUserPut(BaseModel):
    """Модель пользователя для изменения данных"""

    email: EmailStr = None
    password: constr(max_length=255) = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = None
    is_staff: bool = None


class PydenticUserOut(BaseModel):
    """Модель пользователя для выдачи данных"""

    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    last_login: datetime | None
    registration_date: datetime
    is_active: bool
    is_staff: bool
    is_superuser: bool

    class Config:
        from_attributes = True
