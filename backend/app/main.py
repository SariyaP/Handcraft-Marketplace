from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, init_db, settings
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.services.auth import ensure_system_roles


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()

    with SessionLocal() as db:
        ensure_system_roles(db)

    yield

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_env == "development",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Root endpoint")
def read_root() -> dict[str, str]:
    return {
        "message": "Handcraft Marketplace API is running.",
        "docs": "/docs",
        "health": "/health",
    }


app.include_router(health_router)
app.include_router(auth_router)
