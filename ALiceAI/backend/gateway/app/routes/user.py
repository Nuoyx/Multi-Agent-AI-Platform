from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["users"])


@router.get("/me")
async def get_current_user(request: Request):
    try:
        return JSONResponse(
            status_code=200,
            content=request.state.user,
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "get current user error"},
        )

