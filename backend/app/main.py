from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import settings
from app.routers import health

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_env == "development",
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


app.include_router(health.router)
