from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.proxy import proxy_request

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login(request: Request):
    origin = request.headers.get("origin")
    if origin and origin != settings.frontend_url:
        return JSONResponse(
            {"message": "Origin not allowed"},
            status_code=403,
        )

    return await proxy_request(
        request,
        f"{settings.auth_service_url.rstrip('/')}/login",
        service_name="Auth",
        forward_credentials=True,
    )

