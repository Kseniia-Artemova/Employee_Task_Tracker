from datetime import timedelta
from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from app.users.auth import create_access_token, authenticate_user, Login
from app.users.models import User
from app.users.schemas import PydenticUserOut, PydenticUserIn
from app.users import services
from app_config import ACCESS_TOKEN_EXPIRE_MINUTES

users_router = APIRouter()


@users_router.post("/token/")
async def login_for_access_token(credentials: Login):
    user = await authenticate_user(credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get('/', response_model=List[PydenticUserOut])
async def get_users():
    users = await User.all()
    return [PydenticUserOut.model_validate(user) for user in users]


@users_router.post('/', response_model=PydenticUserOut)
async def create_user(user: PydenticUserIn):
    hashed_password = services.hash_password(user.password)
    del user.password
    user_obj = await User.create(**user.model_dump(exclude_unset=True),
                                 password=hashed_password)
    return PydenticUserOut.model_validate(user_obj)


@users_router.get('/{user_id}/', response_model=PydenticUserOut)
async def get_user(user_id: int):
    user_obj = await services.get_user_or_404(user_id)
    return await PydenticUserOut.model_validate(user_obj)


@users_router.put('/{user_id}/', response_model=PydenticUserOut)
async def update_user(user_id: int, user: PydenticUserIn):
    user_obj = await services.get_user_or_404(user_id)
    user_update_data = user.model_dump(exclude_unset=True)
    if 'password' in user_update_data:
        user_update_data['password'] = services.hash_password(user_update_data['password'])
    for key, value in user_update_data.items():
        setattr(user_obj, key, value)
    await user_obj.save()
    return await PydenticUserOut.model_validate(user_obj)


@users_router.delete('/{user_id}/')
async def delete_user(user_id: int):
    user_obj = await services.get_user_or_404(user_id)
    await user_obj.delete()
    return JSONResponse(content={'message': f'Пользователь {user_id} удалён'},
                        status_code=204)
