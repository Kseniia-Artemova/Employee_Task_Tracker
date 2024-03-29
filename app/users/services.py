from fastapi import HTTPException
from app.users.models import User


async def get_user_or_404(user_id: int) -> User:
    """
    Получение пользователя по идентификатору или исключение, если не найден

    :param user_id: идентификатор пользователя
    :return: пользователь или исключение
    """

    user_obj = await User.get_or_none(id=user_id)
    if user_obj is None:
        raise HTTPException(status_code=404, detail=f'Пользователь {user_id} не найден')
    return user_obj