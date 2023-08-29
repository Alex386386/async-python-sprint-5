import os
import shutil
from pathlib import Path
from typing import List

from fastapi import File
from pydantic import BaseModel

from app.schemas.downloaded_file import DownloadedFileDB

VALUE_FOR_RANDOMIZER: int = 10
USER_PASSWORD_LEN: int = 3
stop_folder_name: str = 'files'

BASE_DIR = Path(__file__).parent.parent.parent


class ResponseModel(BaseModel):
    account_id: str
    files: List[DownloadedFileDB]


def delete_file_and_empty_folders(path, stop_folder_name):
    if os.path.isfile(path):
        os.remove(path)

    directory = os.path.dirname(path)
    while os.path.basename(directory) != stop_folder_name:
        if not os.listdir(directory):
            os.rmdir(directory)
        else:
            break
        directory = os.path.dirname(directory)


def create_path(path: str, filename: str) -> Path:
    path = path.lstrip('/')
    file_location = BASE_DIR / 'files' / path
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


def create_file_at_system_address(file_location: Path, filename: str,
                                  file: File):
    if os.path.isdir(file_location):
        file_location = os.path.join(file_location, filename)
    else:
        os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, 'wb+') as buffer:
        shutil.copyfileobj(file.file, buffer)
