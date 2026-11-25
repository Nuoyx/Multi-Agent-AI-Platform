import json

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool


async def auth_middleware(request: Request, call_next):
    try:
        session_id = request.cookies.get("session_id")

        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"message": "unauthorized"},
            )

        session = await run_in_threadpool(
            request.app.state.redis.get,
            f"session-{session_id}",
        )

        if session is None:
            return JSONResponse(
                status_code=400,
                content={"message": "session expired"},
            )

        request.state.user = json.loads(session)

        return await call_next(request)

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "authentication error"},
        )

