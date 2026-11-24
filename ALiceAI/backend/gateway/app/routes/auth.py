import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(request: Request):
    origin = request.headers.get("origin")
    if origin and origin != settings.frontend_url:
        return JSONResponse(
            {"message": "Origin not allowed"},
            status_code=403,
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream = await client.post(
                f"{settings.auth_service_url.rstrip('/')}/login",
                content=await request.body(),
                headers={
                    "Content-Type": request.headers.get(
                        "content-type", "application/json"
                    ),
                    "Cookie": request.headers.get("cookie", ""),
                },
            )
    except httpx.RequestError:
        return JSONResponse(
            {"message": "Auth service is unreachable"},
            status_code=503,
            headers={"Cache-Control": "no-store"},
        )

    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={"Cache-Control": "no-store"},
    )

    if "content-type" in upstream.headers:
        response.headers["Content-Type"] = upstream.headers["content-type"]

    for cookie in upstream.headers.get_list("set-cookie"):
        response.headers.append("Set-Cookie", cookie)

    return response

