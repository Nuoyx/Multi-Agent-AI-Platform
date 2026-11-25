from contextlib import asynccontextmanager

from aliceai_shared.redis.client import create_redis_client

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.routes.auth import router as auth_router
from app.controllers.user_controller import router as user_router
from app.middleware.auth_middleware import auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = create_redis_client(
        settings.redis_url.get_secret_value()
    )
    app.state.redis = redis_client

    try:
        yield
    finally:
        await run_in_threadpool(redis_client.close)


app = FastAPI(
    title="ALiceAI Gateway",
    lifespan=lifespan,
)


@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    if request.url.path.rstrip("/") == "/api/me":
        return await auth_middleware(request, call_next)

    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")

@app.get("/")
async def health():
    return {"service": "gateway", "status": "ok"}
