from typing import List

from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from app.users.models import User
from app.users.schemas import PydenticUserOut, PydenticUserIn
from app.users import services

users_router = APIRouter()


async def get_user_or_404(user_id: int) -> User:
    user_obj = await User.get_or_none(id=user_id)
    if user_obj is None:
        raise HTTPException(status_code=404, detail=f'Пользователь {user_id} не найден')
    return user_obj


@users_router.get('/', response_model=List[PydenticUserOut])
async def get_users():
    users = await User.all()
    return [PydenticUserOut.from_orm(user) for user in users]


@users_router.post('/', response_model=PydenticUserOut)
async def create_user(user: PydenticUserIn):
    hashed_password = services.hash_password(user.password)
    del user.password
    user_obj = await User.create(**user.model_dump(exclude_unset=True),
                                 password=hashed_password)
    return PydenticUserOut.from_orm(user_obj)


@users_router.get('/{user_id}/', response_model=PydenticUserOut)
async def get_user(user_id: int):
    user_obj = await get_user_or_404(user_id)
    return await PydenticUserOut.from_orm(user_obj)


@users_router.put('/{user_id}/', response_model=PydenticUserOut)
async def update_user(user_id: int, user: PydenticUserIn):
    user_obj = await get_user_or_404(user_id)
    user_update_data = user.model_dump(exclude_unset=True)
    if 'password' in user_update_data:
        user_update_data['password'] = services.hash_password(user_update_data['password'])
    for key, value in user_update_data.items():
        setattr(user_obj, key, value)
    await user_obj.save()
    return await PydenticUserOut.from_orm(user_obj)


@users_router.delete('/{user_id}/')
async def delete_user(user_id: int):
    user_obj = await get_user_or_404(user_id)
    await user_obj.delete()
    return JSONResponse(content={'message': f'Пользователь {user_id} удалён'},
                        status_code=204)
