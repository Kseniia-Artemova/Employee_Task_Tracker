from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import JSONResponse

from app.users.auth_utils import create_access_token, authenticate_user, Login, check_superuser_staff_or_owner, \
    check_superuser_or_staff, hash_password
from app.users.models import User
from app.users.schemas import PydenticUserOut, PydenticUserPut, PydenticUserRegister
from app.users import services

users_router = APIRouter()


@users_router.post("/token/")
async def login_for_access_token(credentials: Login) -> dict:
    """
    Вход пользователя и генерация токена доступа

    :param credentials: Учетные данные для входа пользователя
    :return:  Словарь с токеном доступа и типом токена
    """

    user = await authenticate_user(credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})

    user.last_login = datetime.utcnow()
    await user.save()

    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get('/', response_model=List[PydenticUserOut])
async def get_users(current_user: User = Depends(check_superuser_or_staff)) -> List[User]:  # noqa: F841
    """
    Получить список пользователей

    :param current_user: текущий пользователь
    :return: список пользователей
    """

    users = await User.all()
    return users


@users_router.post('/', response_model=PydenticUserOut)
async def create_user(user: PydenticUserRegister) -> User:
    """
    Создание нового пользователя

    :param user: данные пользователя
    :return: созданный пользователь
    """

    hashed_password = hash_password(user.password)
    del user.password
    user_obj = await User.create(**user.model_dump(exclude_unset=True),
                                 password=hashed_password)
    return user_obj


@users_router.get('/{user_id}/', response_model=PydenticUserOut)
async def get_user(user_id: int, current_user: User = Depends(check_superuser_staff_or_owner)) -> User:  # noqa: F841
    """
    Получить пользователя по идентификатору

    :param user_id: идентификатор пользователя
    :param current_user: текущий пользователь
    :return: пользователь
    """

    user_obj = await services.get_user_or_404(user_id)
    return user_obj


@users_router.put('/{user_id}/', response_model=PydenticUserOut)
async def update_user(user_id: int, user: PydenticUserPut,
                      current_user: User = Depends(check_superuser_staff_or_owner)) -> User:  # noqa: F841
    """
    Обновление информации о пользователе

    :param user_id: идентификатор пользователя
    :param user: данные пользователя
    :param current_user: текущий пользователь
    :return: обновленный пользователь
    """

    user_obj = await services.get_user_or_404(user_id)

    if not current_user.is_superuser:
        del user.is_staff
        del user.is_active

    user_update_data = user.model_dump(exclude_unset=True)
    if 'password' in user_update_data:
        user_update_data['password'] = hash_password(user_update_data['password'])
    for key, value in user_update_data.items():
        setattr(user_obj, key, value)
    await user_obj.save()
    return user_obj


@users_router.delete('/{user_id}/')
async def delete_user(user_id: int, current_user: User = Depends(check_superuser_staff_or_owner)) -> JSONResponse:  # noqa: F841
    """
    Удаление пользователя по идентификатору

    :param user_id: идентификатор пользователя
    :param current_user: текущий пользователь
    :return: сообщение об удалении
    """
    user_obj = await services.get_user_or_404(user_id)
    await user_obj.delete()
    content = {'message': f'Пользователь {user_id} удалён'}

    return JSONResponse(content=content, status_code=200)
