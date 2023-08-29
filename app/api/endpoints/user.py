from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import auth_backend, fastapi_users, current_superuser
from app.core.utils import stop_folder_name, delete_file_and_empty_folders
from app.crud.downloaded_file import downloaded_file_crud
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
    prefix='/users',
    tags=['users'],
)


@router.delete(
    '/users/{id}',
    tags=['users'],
    deprecated=True
)
def delete_user(id: str):
    raise HTTPException(
        status_code=405,
        detail="Удаление пользователей запрещено!"
    )


@router.delete(
    '/user/{user_id}',
    tags=['user'],
    dependencies=[Depends(current_superuser)],
    description='Удалить пользователя и все его файлы. Доступно только суперюзеру.',
)
async def delete_user_by_id(
        user_id: UUID4,
        session: AsyncSession = Depends(get_async_session),
):
    user = await session.execute(
        select(User).where(
            User.id == user_id
        )
    )
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    my_files = await downloaded_file_crud.get_my(user_id, session)
    if my_files:
        for file_obj in my_files:
            delete_file_and_empty_folders(file_obj.path, stop_folder_name)
    await session.delete(user)
    await session.commit()
    return {'status': f'User {user_id} and all their files were deleted!'}
