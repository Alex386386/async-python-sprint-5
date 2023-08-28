import os
import shutil
from http import HTTPStatus
from typing import Optional

from fastapi import (
    APIRouter, UploadFile, File, Depends, HTTPException, Body, Query,
)
from fastapi.responses import FileResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_path_correct, check_unique_file_name, path_validation,
    check_exists, check_the_opportunity_to_delete
)
from app.core.db import get_async_session
from app.core.user import current_user
from app.core.utils import (
    BASE_DIR, stop_folder_name,
    delete_file_and_empty_folders, ResponseModel
)
from app.crud.downloaded_file import downloaded_file_crud
from app.models import User
from app.schemas.downloaded_file import DownloadedFileDB

router = APIRouter()


@router.get(
    '/',
    response_model=ResponseModel,
)
async def get_my_files(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    files = await downloaded_file_crud.get_my(user=user, session=session)
    return {'account_id': f'{user.id}', 'files': files}


@router.post(
    '/upload',
    response_model=DownloadedFileDB
)
async def upload_file(
        path: str = Body('/', example='/homework/test-folder/notes.txt'),
        file: UploadFile = File(...),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    filename = file.filename
    path = path.lstrip('/')
    file_location = BASE_DIR / 'files' / path
    file_location = check_path_correct(file_location, filename)
    await check_unique_file_name(filename, session)
    if os.path.isdir(file_location):
        file_location = os.path.join(file_location, filename)
    else:
        os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, 'wb+') as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_size = os.path.getsize(file_location)

    db_file = await downloaded_file_crud.upload_file(
        file_name=filename,
        path=str(file_location),
        size=file_size,
        user=user,
        session=session
    )
    return db_file


@router.get(
    '/download',
    dependencies=[Depends(current_user)],
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
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Файла с таким id не существует'
            )
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Необходимо предоставить либо путь к файлу, либо id файла!'
        )

    if not os.path.isfile(file_location):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Объект по данному адресу не существует!'
        )
    return FileResponse(file_location,
                        filename=os.path.basename(file_location))


@router.delete('/{file_id}')
async def remove_file(
        file_id: UUID4,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    file_obj = await check_exists(file_id, session)
    await check_the_opportunity_to_delete(file_obj, user)
    file_obj = await downloaded_file_crud.remove(file_obj, session)
    name = file_obj.name
    delete_file_and_empty_folders(file_obj.path, stop_folder_name)
    return {'status': f'File {name} was delete!'}


@router.delete('/')
async def remove_all_my_files(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    my_files = await downloaded_file_crud.get_my(user, session)
    if not my_files:
        return {'status': 'You do not have any files to delete!'}
    for file_obj in my_files:
        file_obj = await downloaded_file_crud.remove(file_obj, session)
        delete_file_and_empty_folders(file_obj.path, stop_folder_name)
    return {'status': 'All files were deleted!'}
