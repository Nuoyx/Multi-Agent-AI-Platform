import json
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from firebase_admin import auth
from redis.exceptions import RedisError

from app.schemas import LoginRequest
from app.services.firebase_service import verify_firebase_token
from app.services.user_service import get_user

router = APIRouter(tags=["auth"])
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60


@router.post("/login")
def login(body: LoginRequest, request: Request):
    headers = {"Cache-Control": "no-store"}

    try:
        claims = verify_firebase_token(
            body.token,
            request.app.state.firebase_app,
        )
    except auth.InvalidIdTokenError:
        return JSONResponse(
            {"message": "Invalid or expired Firebase token"},
            status_code=401,
            headers=headers,
        )
    except auth.CertificateFetchError:
        return JSONResponse(
            {"message": "Firebase verification temporarily unavailable"},
            status_code=503,
            headers=headers,
        )

    user = get_user(claims)
    session_id = str(uuid.uuid4())

    try:
        request.app.state.redis.set(
            f"session-{session_id}",
            json.dumps({
                "userId": user["firebaseUid"],
                "name": user["name"],
                "email": user["email"],
                "avatar": user["avatar"],
            }),
            ex=SESSION_TTL_SECONDS,
        )
    except RedisError:
        return JSONResponse(
            {"message": "Session storage temporarily unavailable"},
            status_code=503,
            headers=headers,
        )

    response = JSONResponse(user, headers=headers)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=SESSION_TTL_SECONDS,
        path='/'
    )

    return response


@router.post("/logout")
def logout(request: Request):
    headers = {"Cache-Control": "no-store"}
    session_id = request.cookies.get("session_id")

    try:
        if session_id:
            request.app.state.redis.delete(f"session-{session_id}")

        response = JSONResponse(
            {"message": "logout successfully."},
            status_code=200,
            headers=headers,
        )
        response.delete_cookie(
            key="session_id",
            path="/",
            httponly=True,
            secure=False,
            samesite="strict",
        )
        return response
    except Exception:
        return JSONResponse(
            {"message": "Logout failed."},
            status_code=500,
            headers=headers,
        )

