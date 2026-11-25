from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utc_now


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.conversations.id"), index=True
    )
    content: Mapped[str] = mapped_column(Text)
    role: Mapped[MessageRole] = mapped_column(
        SqlEnum(
            MessageRole,
            values_callable=lambda roles: [role.value for role in roles],
            name="message_role",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        )
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, server_default=func.now(), onupdate=utc_now
    )
