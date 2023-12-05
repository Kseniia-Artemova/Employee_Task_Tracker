from datetime import datetime

from pydantic import BaseModel, EmailStr


class PydenticUserIn(BaseModel):
    """Модель пользователя для получения данных"""

    email: EmailStr
    password: str
    first_name: str
    last_name: str
    is_active: bool = True
    is_stuff: bool = False
    is_superuser: bool = False


class PydenticUserOut(BaseModel):
    """Модель пользователя для выдачи данных"""

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    last_login: datetime | None
    registration_date: datetime
    is_active: bool
    is_stuff: bool
    is_superuser: bool

    class Config:
        from_attributes = True