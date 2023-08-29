import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from app.core.db import Base


class DownloadedFile(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime)
    path = Column(String(100))
    size = Column(Integer)
    is_downloadable = Column(Boolean, default=True, nullable=False)
    user_id = Column(
        UUIDType,
        ForeignKey('user.id', name='fk_shorturl_user_id_user'),
        nullable=False,
    )
    user = relationship('User', back_populates='downloaded_files')
