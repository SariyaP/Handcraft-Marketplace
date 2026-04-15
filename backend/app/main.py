from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, init_db, settings
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.commissions import router as commissions_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.makers import router as makers_router
from app.routers.products import maker_router as maker_products_router
from app.routers.products import router as products_router
from app.routers.reviews import router as reviews_router
from app.routers.wishlist import router as wishlist_router
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
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(commissions_router)
app.include_router(dashboard_router)
app.include_router(makers_router)
app.include_router(products_router)
app.include_router(maker_products_router)
app.include_router(reviews_router)
app.include_router(wishlist_router)
