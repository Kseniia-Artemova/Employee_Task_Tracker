from datetime import datetime

from pydantic import BaseModel, EmailStr, constr, model_validator


class PydenticUserRegister(BaseModel):
    """Модель пользователя для получения данных при регистрации"""

    email: EmailStr
    password: constr(max_length=255)
    password2: constr(max_length=255)
    first_name: str | None = None
    last_name: str | None = None

    @model_validator(mode='after')
    def check_passwords_match(self):
        """Проверяет, совпадают ли два пароля."""

        pw1, pw2 = self.password, self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Пароли не совпадают')
        return self

    class Config:
        from_attributes = True


class PydenticUserPut(BaseModel):
    """Модель пользователя для изменения данных"""

    email: EmailStr = None
    password: constr(max_length=255) = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = None
    is_staff: bool = None

    class Config:
        from_attributes = True


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
