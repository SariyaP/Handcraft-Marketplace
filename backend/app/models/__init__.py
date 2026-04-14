"""Database models package."""

from app.models.marketplace import (
    Commission,
    MakerProfile,
    Product,
    Review,
    Role,
    ShopVerification,
    User,
    Wishlist,
    WipUpdate,
)


def load_all_models() -> None:
    """Import models so SQLAlchemy registers them on the metadata."""


__all__ = [
    "Commission",
    "MakerProfile",
    "Product",
    "Review",
    "Role",
    "ShopVerification",
    "User",
    "Wishlist",
    "WipUpdate",
    "load_all_models",
]
