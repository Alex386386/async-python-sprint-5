import os
from pathlib import Path
from typing import List

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
