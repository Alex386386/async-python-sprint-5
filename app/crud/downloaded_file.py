from datetime import datetime
from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import DownloadedFile


class CRUDDownloadedFile(CRUDBase):

    async def get_my(
            self,
            user_id: UUID4,
            session: AsyncSession,
    ) -> List[DownloadedFile]:
        files = await session.execute(
            select(DownloadedFile).where(
                DownloadedFile.user_id == user_id
            )
        )
        return files.scalars().all()

    async def upload_file(
            self,
            file_name,
            path,
            size,
            user,
            session: AsyncSession,
    ):
        obj_in_data = dict()
        obj_in_data['name'] = file_name
        obj_in_data['created_at'] = datetime.now()
        obj_in_data['path'] = path
        obj_in_data['size'] = size
        obj_in_data['is_downloadable'] = True
        obj_in_data['user_id'] = user.id
        db_file = self.model(**obj_in_data)

        session.add(db_file)
        await session.commit()
        await session.refresh(db_file)
        return db_file

    async def get_file_id_by_name(
            self,
            filename: str,
            session: AsyncSession,
    ) -> Optional[DownloadedFile]:
        url = await session.execute(
            select(DownloadedFile.id).where(
                DownloadedFile.name == filename
            )
        )
        return url.scalars().first()

    async def get_file_location_by_id(
            self,
            file_id: UUID4,
            session: AsyncSession,
    ) -> Optional[DownloadedFile]:
        path = await session.execute(
            select(DownloadedFile.path).where(
                DownloadedFile.id == file_id
            )
        )
        return path.scalars().first()


downloaded_file_crud = CRUDDownloadedFile(DownloadedFile)
