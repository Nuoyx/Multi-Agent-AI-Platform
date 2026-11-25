from contextlib import asynccontextmanager

import firebase_admin
from fastapi import FastAPI
from aliceai_shared.redis.client import create_redis_client

from app.config import settings
from app.config.firebase import initialize_firebase
from app.routes.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_app = initialize_firebase()
    app.state.firebase_app = firebase_app

    try:
        with create_redis_client(settings.redis_url.get_secret_value()) as redis_client:
            app.state.redis = redis_client
            yield
    finally:
        firebase_admin.delete_app(firebase_app)


app = FastAPI(title="ALiceAI Auth Service", lifespan=lifespan)
app.include_router(auth_router)

@app.get("/")
def health():
    return {"service": "auth", "status": "ok"}

