from datetime import datetime

from pydantic import BaseModel, UUID4


class DownloadedFileBase(BaseModel):
    path: str


class DownloadedFileDB(DownloadedFileBase):
    id: UUID4
    name: str
    created_at: datetime
    path: str
    size: int
    is_downloadable: bool

    class Config:
        orm_mode = True
