from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from app.config.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await run_in_threadpool(engine.dispose)


app = FastAPI(title="ALiceAI Agent Service", lifespan=lifespan)


@app.get("/")
def health():
    return {"service": "agent", "status": "ok"}
