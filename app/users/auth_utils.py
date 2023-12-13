from datetime import timedelta, datetime
from typing import Optional

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from app.users.models import User
from app.config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Login(BaseModel):
    email: EmailStr
    password: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(email: str, password: str) -> Optional[User]:
    user = await User.get_or_none(email=email)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        token_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = token_info.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Пользователь не авторизован")
        user = await User.get(email=user_email)
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")


async def check_superuser_staff_or_owner(user_id: int, current_user: User = Security(get_current_user)) -> User:
    if current_user.is_active and any((current_user.is_superuser, current_user.is_staff, current_user.id == user_id)):
        return current_user
    raise HTTPException(status_code=403, detail="Текущее действие запрещено")


async def check_superuser_or_staff(current_user: User = Security(get_current_user)) -> User:
    if (current_user.is_superuser or current_user.is_staff) and current_user.is_active:
        return current_user
    raise HTTPException(status_code=403, detail="Текущее действие запрещено")
