import os
from typing import Optional

from fastapi import (
    APIRouter, UploadFile, File, Depends, Body, Query,
)
from fastapi.responses import FileResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_unique_file_name, path_validation,
    check_exists, check_the_opportunity_to_delete,
    parameters_were_not_provided, check_exist_file, object_is_not_exist
)
from app.core.db import get_async_session
from app.core.user import current_user
from app.core.utils import (
    stop_folder_name,
    delete_file_and_empty_folders, ResponseModel, create_path,
    create_file_at_system_address
)
from app.crud.downloaded_file import downloaded_file_crud
from app.models import User
from app.schemas.downloaded_file import DownloadedFileDB

router = APIRouter()


@router.get(
    '/',
    response_model=ResponseModel,
    description='Получить информацию о всей файлах, авторизованного пользователя, загруженных на сервер.',
)
async def get_my_files(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    files = await downloaded_file_crud.get_my(user_id=user.id, session=session)
    return {'account_id': f'{user.id}', 'files': files}


@router.post(
    '/upload',
    response_model=DownloadedFileDB,
    description='Загрузить файл на сервер, доступно только авторизованному пользователю.',
)
async def upload_file(
        path: str = Body('/', example='/homework/test-folder/notes.txt'),
        file: UploadFile = File(...),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    filename = file.filename
    file_location = create_path(path, filename)

    await check_unique_file_name(filename, session)

    create_file_at_system_address(
        file_location=file_location, filename=filename, file=file)

    file_size = os.path.getsize(file_location)

    db_file = await downloaded_file_crud.upload_file(
        file_name=filename, path=str(file_location), size=file_size, user=user,
        session=session
    )
    return db_file


@router.get(
    '/download',
    description='Загрузить файл на локальный компьютер.'
                ' Используйте либо полный путь файла, либо его id.',
)
async def download_file(
        path: Optional[str] = Query(None),
        file_id: Optional[UUID4] = Query(None),
        session: AsyncSession = Depends(get_async_session)
):
    if path:
        path = path.lstrip('/')
        file_location = path_validation(path)
    elif file_id:
        file_location = await downloaded_file_crud.get_file_location_by_id(
            file_id, session
        )
        if not file_location:
            object_is_not_exist()
    else:
        parameters_were_not_provided()

    check_exist_file(file_location)
    return FileResponse(file_location,
                        filename=os.path.basename(file_location))


@router.delete(
    '/{file_id}',
    description='Удалить файл по id, доступно авторизованному пользователю.'
                ' Удалять можно только свои файлы',
)
async def remove_file(
        file_id: UUID4,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    file_obj = await check_exists(file_id, session)
    await check_the_opportunity_to_delete(file_obj, user)
    file_obj = await downloaded_file_crud.remove(file_obj, session)
    delete_file_and_empty_folders(file_obj.path, stop_folder_name)
    name = file_obj.name
    return {'status': f'File {name} was delete!'}


@router.delete(
    '/',
    description='Удалить все файлы авторизованного пользователя.'
)
async def remove_all_my_files(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    my_files = await downloaded_file_crud.get_my(
        user_id=user.id, session=session
    )
    if not my_files:
        return {'status': 'You do not have any files to delete!'}
    for file_obj in my_files:
        file_obj = await downloaded_file_crud.remove(file_obj, session)
        delete_file_and_empty_folders(file_obj.path, stop_folder_name)
    return {'status': 'All files were deleted!'}
