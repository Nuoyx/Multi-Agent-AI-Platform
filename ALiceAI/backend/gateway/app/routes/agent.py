from fastapi import APIRouter, Request

from app.config import settings
from app.utils.proxy import proxy_request

router = APIRouter(tags=["agent"])


@router.get("")
@router.post("")
@router.get("/{path:path}")
@router.post("/{path:path}")
async def forward_agent(request: Request, path: str = ""):
    return await proxy_request(
        request,
        f"{settings.agent_service_url.rstrip('/')}/{path}",
        service_name="Agent",
        forward_user=True,
    )
