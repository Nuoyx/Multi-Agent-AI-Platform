from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utc_now


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(
        Text, default="New Chat", server_default="New Chat"
    )
    user_id: Mapped[str] = mapped_column(Text, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now(), onupdate=utc_now
    )
