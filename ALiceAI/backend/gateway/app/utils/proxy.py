from uuid import uuid4

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, Response


async def proxy_request(
    request: Request,
    upstream_url: str,
    *,
    service_name: str,
    forward_credentials: bool = False,
    forward_user: bool = False,
) -> Response:
    """Forward a buffered request to a server-controlled upstream URL.

    Identity comes only from authentication middleware. Services receiving it
    must restrict access to trusted gateway connections.
    """
    request_id = str(uuid4())
    headers = {
        "Content-Type": request.headers.get("content-type", "application/json"),
        "X-Request-ID": request_id,
    }
    if "accept" in request.headers:
        headers["Accept"] = request.headers["accept"]
    if forward_credentials:
        for name in ("cookie", "authorization"):
            if name in request.headers:
                headers[name] = request.headers[name]
    if forward_user:
        user = getattr(request.state, "user", None)
        if not user or not user.get("userId"):
            raise HTTPException(status_code=401, detail="Authentication required")
        headers["X-User-ID"] = user["userId"]

    response_headers = {"Cache-Control": "no-store", "X-Request-ID": request_id}
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            upstream = await client.request(
                method=request.method,
                url=upstream_url,
                params=request.query_params.multi_items(),
                content=await request.body(),
                headers=headers,
            )
    except httpx.RequestError:
        return JSONResponse(
            {"message": f"{service_name} service is unreachable"},
            status_code=503,
            headers=response_headers,
        )

    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
    if "content-type" in upstream.headers:
        response.headers["Content-Type"] = upstream.headers["content-type"]
    if forward_credentials:
        for cookie in upstream.headers.get_list("set-cookie"):
            response.headers.append("Set-Cookie", cookie)
    return response
