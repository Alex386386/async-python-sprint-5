from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import relationship

from app.core.db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    downloaded_files = relationship(
        'DownloadedFile',
        back_populates='user',
        cascade='all, delete-orphan'
    )
