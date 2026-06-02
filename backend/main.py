from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.clusters import router as clusters_router
from api.export import router as export_router
from api.health import router as health_router
from api.history import router as history_router
from api.investigate import router as investigate_router
from core.config import settings
from core.logging import log_startup, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    log_startup()
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(clusters_router)
app.include_router(investigate_router)
app.include_router(history_router)
app.include_router(export_router)
