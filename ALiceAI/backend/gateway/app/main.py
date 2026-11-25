from contextlib import asynccontextmanager

from aliceai_shared.redis.client import create_redis_client

from fastapi import FastAPI, Request
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.config.cors import configure_cors
from app.routes.agent import router as agent_router
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.user import router as user_router
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
    path = request.url.path.rstrip("/")
    if (
        path == "/api/me"
        or path.startswith("/api/chat/")
        or path == "/api/agent"
        or path.startswith("/api/agent/")
    ):
        return await auth_middleware(request, call_next)

    return await call_next(request)

configure_cors(app)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(user_router, prefix="/api/me")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(agent_router, prefix="/api/agent")


@app.get("/")
async def health():
    return {"service": "gateway", "status": "ok"}
