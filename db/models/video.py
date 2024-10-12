import uuid
from datetime import datetime

from db.database import Base
from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime
from sqlalchemy.ext.compiler import compiles


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


#pk_id = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
created_at = Annotated[datetime, mapped_column(server_default=utcnow(), default=utcnow())]
updated_at = Annotated[datetime, mapped_column(default=utcnow(), server_default=utcnow(), onupdate=utcnow(), server_onupdate=utcnow())]
pk_id = Annotated[uuid.UUID, mapped_column(primary_key=True, index=True, default=uuid.uuid4)]


class AttributeMixin:
    id: Mapped[pk_id]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Camera(Base, AttributeMixin):
    __tablename__ = "camera"
    threadURL: Mapped[str] = mapped_column(String(255), nullable=False)

class Video(Base, AttributeMixin):
    __tablename__ = "video"

    path: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    state: Mapped[str] = mapped_column(String(255), nullable=False, default="NonHandled")
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    content_length: Mapped[int] = mapped_column(nullable=False)


class VideoLog(Base, AttributeMixin):
    __tablename__ = "video_log"

    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("video.id"), nullable=False)
    exception: Mapped[str] = mapped_column(String(255), nullable=False)
    attempt: Mapped[int] = mapped_column(nullable=False)
    is_looped: Mapped[bool] = mapped_column(nullable=False)