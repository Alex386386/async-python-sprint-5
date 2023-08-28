from http import HTTPStatus
from pathlib import Path

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import BASE_DIR
from app.crud.downloaded_file import downloaded_file_crud
from app.models import DownloadedFile, User


def check_path_correct(
        file_location: Path,
        filename: str,
) -> Path:
    if str(file_location).endswith('/'):
        return file_location / filename
    elif not str(file_location).endswith('/'):
        last_element = str(file_location).split('/')[-1]
        if '.' in last_element:
            directories = str(file_location).split('/')
            directories.pop()
            file_location = '/'.join(directory for directory in directories)
            return Path(file_location)
        if last_element != filename:
            file_location = file_location / filename
    return file_location


def path_validation(
        path: str,
) -> Path:
    if path == '':
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы не указали имя файла!',
        )
    path_preparation = BASE_DIR / 'files'
    check_preparation = str(path_preparation).lstrip('/')
    if check_preparation not in path:
        path = path_preparation / path
    if str(path).endswith('/') or '.' not in str(path).split('/')[-1]:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы не указали имя файла!',
        )
    path = '/' + str(path)
    path = Path(path)
    return path


async def check_exists(
        obj_id: UUID4,
        session: AsyncSession,
):
    model_object = await downloaded_file_crud.get(obj_id, session)
    if model_object is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Объект не существует!'
        )
    return model_object


async def check_the_opportunity_to_delete(
        downloaded_file: DownloadedFile,
        user: User,
):
    if downloaded_file.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Вы не можете удалить файл которым вы не владеете!'
        )


async def check_unique_file_name(
        filename: str,
        session: AsyncSession,
) -> None:
    file_id = await downloaded_file_crud.get_file_id_by_name(filename, session)
    if file_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Объект с таким именем уже существует',
        )
