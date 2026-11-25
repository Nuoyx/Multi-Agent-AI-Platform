from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.models import MessageRole
from app.services import conversation_service, message_service

router = APIRouter(tags=["chat"])


class UpdateConversationRequest(BaseModel):
    id: UUID
    title: str


class SaveMessageRequest(BaseModel):
    conversation_id: UUID = Field(alias="conversationId")
    role: MessageRole
    content: str


class GetMessageRequest(BaseModel):
    conversation_id: UUID = Field(alias="conversationId")


def error_response(message: str, error: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": message, "error": type(error).__name__},
    )


@router.get("/create-conversation")
def create_conversation(request: Request):
    try:
        user_id = request.headers.get("x-user-id")
        conversation = conversation_service.create_conversation(user_id)
        return JSONResponse(status_code=200, content={"conversation": conversation})
    except Exception as error:
        return error_response("create conversation error", error)


@router.get("/get-conversations")
def get_conversations(request: Request):
    try:
        user_id = request.headers.get("x-user-id")
        conversations = conversation_service.get_conversations(user_id)
        return JSONResponse(status_code=200, content={"conversation": conversations})
    except Exception as error:
        return error_response("get conversation error", error)


@router.post("/update-conversation")
def update_conversation(body: UpdateConversationRequest):
    try:
        conversation = conversation_service.update_conversation(body.id, body.title)
        return JSONResponse(status_code=200, content={"conversation": conversation})
    except Exception as error:
        return error_response("update conversation error", error)


@router.post("/save-message")
def save_message(body: SaveMessageRequest):
    try:
        message = message_service.create_message(
            body.conversation_id, body.role, body.content
        )
        return JSONResponse(status_code=200, content={"message": message})
    except Exception as error:
        return error_response("save message error", error)


@router.post("/get-message")
def get_message(body: GetMessageRequest):
    try:
        messages = message_service.get_messages(body.conversation_id)
        return JSONResponse(status_code=200, content={"message": messages})
    except Exception as error:
        return error_response("get messages error", error)
