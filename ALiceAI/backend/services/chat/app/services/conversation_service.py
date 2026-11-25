from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from app.config.database import SessionLocal
from app.models import Conversation


def serialize_conversation(conversation: Conversation) -> dict:
    return jsonable_encoder({
        "id": conversation.id,
        "title": conversation.title,
        "userId": conversation.user_id,
        "createdAt": conversation.created_at,
        "updatedAt": conversation.updated_at,
    })


def create_conversation(user_id: str) -> dict:
    with SessionLocal.begin() as db:
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        db.flush()
        result = serialize_conversation(conversation)
    return result


def get_conversations(user_id: str) -> list[dict]:
    with SessionLocal() as db:
        conversations = db.scalars(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        ).all()
        return [serialize_conversation(item) for item in conversations]


def update_conversation(conversation_id: UUID, title: str) -> dict | None:
    with SessionLocal.begin() as db:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            return None
        conversation.title = title
        db.flush()
        result = serialize_conversation(conversation)
    return result
