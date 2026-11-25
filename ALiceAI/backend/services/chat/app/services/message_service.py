from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from app.config.database import SessionLocal
from app.models import Message, MessageRole


def serialize_message(message: Message) -> dict:
    return jsonable_encoder({
        "id": message.id,
        "conversationId": message.conversation_id,
        "role": message.role,
        "content": message.content,
        "createdAt": message.created_at,
        "updatedAt": message.updated_at,
    })


def create_message(conversation_id: UUID, role: MessageRole, content: str) -> dict:
    with SessionLocal.begin() as db:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(message)
        db.flush()
        result = serialize_message(message)
    return result


def get_messages(conversation_id: UUID) -> list[dict]:
    with SessionLocal() as db:
        messages = db.scalars(
            select(Message).where(Message.conversation_id == conversation_id)
        ).all()
        return [serialize_message(item) for item in messages]
