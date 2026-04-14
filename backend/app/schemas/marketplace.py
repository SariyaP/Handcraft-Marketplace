from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase, ORMBaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True


class UserCreate(UserBase):
    role_id: int
    password_hash: str


class UserRead(UserBase, ORMBaseModel):
    id: int
    role_id: int
    created_at: datetime
    updated_at: datetime


class MakerProfileBase(BaseModel):
    shop_name: str
    bio: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class MakerProfileCreate(MakerProfileBase):
    user_id: int


class MakerProfileRead(MakerProfileBase, ORMBaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    is_active: bool = True


class ProductCreate(ProductBase):
    maker_id: int


class ProductRead(ProductBase, ORMBaseModel):
    id: int
    maker_id: int
    created_at: datetime
    updated_at: datetime


class CommissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    budget: Optional[Decimal] = None
    status: str = "pending"


class CommissionCreate(CommissionBase):
    customer_id: int
    maker_id: int


class CommissionRead(CommissionBase, ORMBaseModel):
    id: int
    customer_id: int
    maker_id: int
    created_at: datetime
    updated_at: datetime


class WipUpdateBase(BaseModel):
    message: str
    image_url: Optional[str] = None


class WipUpdateCreate(WipUpdateBase):
    commission_id: int


class WipUpdateRead(WipUpdateBase, ORMBaseModel):
    id: int
    commission_id: int
    created_at: datetime


class WishlistBase(BaseModel):
    customer_id: int
    product_id: int


class WishlistCreate(WishlistBase):
    pass


class WishlistRead(WishlistBase, ORMBaseModel):
    id: int
    created_at: datetime


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    customer_id: int
    product_id: Optional[int] = None
    commission_id: Optional[int] = None


class ReviewRead(ReviewBase, ORMBaseModel):
    id: int
    customer_id: int
    product_id: Optional[int] = None
    commission_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ShopVerificationBase(BaseModel):
    document_url: Optional[str] = None
    status: str = "pending"
    notes: Optional[str] = None


class ShopVerificationCreate(ShopVerificationBase):
    maker_id: int


class ShopVerificationRead(ShopVerificationBase, ORMBaseModel):
    id: int
    maker_id: int
    created_at: datetime
    updated_at: datetime
