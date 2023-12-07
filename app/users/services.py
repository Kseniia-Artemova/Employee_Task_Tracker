from fastapi import HTTPException
from passlib.context import CryptContext

from app.users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def get_user_or_404(user_id: int) -> User:
    user_obj = await User.get_or_none(id=user_id)
    if user_obj is None:
        raise HTTPException(status_code=404, detail=f'Пользователь {user_id} не найден')
    return user_obj