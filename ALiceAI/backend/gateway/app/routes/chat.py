from fastapi import APIRouter, Request

from app.config import settings
from app.utils.proxy import proxy_request

router = APIRouter(tags=["chat"])


@router.get("/create-conversation")
@router.get("/get-conversations")
@router.post("/update-conversation")
@router.post("/save-message")
@router.post("/get-message")
async def forward_chat(request: Request):
    path = request.url.path.removeprefix("/api/chat")
    return await proxy_request(
        request,
        f"{settings.chat_service_url.rstrip('/')}{path}",
        service_name="Chat",
        forward_user=True,
    )
