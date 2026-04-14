from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class Role(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role: Mapped["Role"] = relationship(back_populates="users")
    maker_profile: Mapped[Optional["MakerProfile"]] = relationship(
        back_populates="maker",
        uselist=False,
    )
    products: Mapped[list["Product"]] = relationship(back_populates="maker")
    customer_commissions: Mapped[list["Commission"]] = relationship(
        back_populates="customer",
        foreign_keys="Commission.customer_id",
    )
    maker_commissions: Mapped[list["Commission"]] = relationship(
        back_populates="maker",
        foreign_keys="Commission.maker_id",
    )
    wishlists: Mapped[list["Wishlist"]] = relationship(back_populates="customer")
    reviews: Mapped[list["Review"]] = relationship(back_populates="customer")
    shop_verifications: Mapped[list["ShopVerification"]] = relationship(back_populates="maker")


class MakerProfile(TimestampMixin, Base):
    __tablename__ = "maker_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    shop_name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(150))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))

    maker: Mapped["User"] = relationship(back_populates="maker_profile")


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    maker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    maker: Mapped["User"] = relationship(back_populates="products")
    wishlists: Mapped[list["Wishlist"]] = relationship(back_populates="product")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")


class Commission(TimestampMixin, Base):
    __tablename__ = "commissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    maker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    customer: Mapped["User"] = relationship(
        back_populates="customer_commissions",
        foreign_keys=[customer_id],
    )
    maker: Mapped["User"] = relationship(
        back_populates="maker_commissions",
        foreign_keys=[maker_id],
    )
    wip_updates: Mapped[list["WipUpdate"]] = relationship(back_populates="commission")
    reviews: Mapped[list["Review"]] = relationship(back_populates="commission")


class WipUpdate(TimestampMixin, Base):
    __tablename__ = "wip_updates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    commission_id: Mapped[int] = mapped_column(
        ForeignKey("commissions.id"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))

    commission: Mapped["Commission"] = relationship(back_populates="wip_updates")


class Wishlist(TimestampMixin, Base):
    __tablename__ = "wishlists"
    __table_args__ = (
        UniqueConstraint("customer_id", "product_id", name="uq_wishlist_customer_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)

    customer: Mapped["User"] = relationship(back_populates="wishlists")
    product: Mapped["Product"] = relationship(back_populates="wishlists")


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint(
            "(product_id IS NOT NULL AND commission_id IS NULL) OR "
            "(product_id IS NULL AND commission_id IS NOT NULL)",
            name="ck_reviews_target",
        ),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"))
    commission_id: Mapped[Optional[int]] = mapped_column(ForeignKey("commissions.id"))
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    customer: Mapped["User"] = relationship(back_populates="reviews")
    product: Mapped[Optional["Product"]] = relationship(back_populates="reviews")
    commission: Mapped[Optional["Commission"]] = relationship(back_populates="reviews")


class ShopVerification(TimestampMixin, Base):
    __tablename__ = "shop_verifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    maker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    document_url: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    maker: Mapped["User"] = relationship(back_populates="shop_verifications")
