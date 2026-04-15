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
    specialization: Optional[str] = None
    profile_image_url: Optional[str] = None
    verification_status: str = "unverified"
    location: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class MakerProfileCreate(MakerProfileBase):
    user_id: int


class MakerProfileRead(MakerProfileBase, ORMBaseModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class MakerProfileUpdateRequest(BaseModel):
    shop_name: str = Field(min_length=1, max_length=150)
    bio: Optional[str] = None
    specialization: Optional[str] = Field(default=None, max_length=150)
    profile_image_url: Optional[str] = Field(default=None, max_length=255)


class MakerProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    shop_name: str
    bio: Optional[str] = None
    specialization: Optional[str] = None
    profile_image_url: Optional[str] = None
    verification_status: str
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


class MakerProductCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = True


class MakerProductUpdateRequest(MakerProductCreateRequest):
    pass


class MakerProductResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    maker_id: int
    maker_name: str


class ProductCustomizationChoiceRead(BaseModel):
    id: int
    label: str
    price_delta: Decimal


class ProductCustomizationOptionRead(BaseModel):
    id: int
    name: str
    is_required: bool
    choices: list[ProductCustomizationChoiceRead]


class ProductDetailResponse(ProductListItem):
    stock_quantity: int
    is_active: bool
    customization_options: list[ProductCustomizationOptionRead]
    reviews: list["ReviewListItem"]
    created_at: datetime
    updated_at: datetime


class CommissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    customization_notes: Optional[str] = None
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


class CommissionStatus(str):
    pass


class CreateCommissionRequest(BaseModel):
    maker_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    customization_notes: Optional[str] = None
    budget: Optional[Decimal] = Field(default=None, ge=0)


class UpdateCommissionStatusRequest(BaseModel):
    status: str = Field(pattern="^(pending|accepted|rejected|in_progress|completed)$")


class CommissionListItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    customization_notes: Optional[str] = None
    budget: Optional[Decimal] = None
    status: str
    customer_id: int
    customer_name: str
    maker_id: int
    maker_name: str
    wip_updates: list["WipUpdateRead"] = []
    created_at: datetime
    updated_at: datetime


class WipUpdateBase(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    image_url: Optional[str] = None


class WipUpdateCreate(WipUpdateBase):
    pass


class WipUpdateRead(WipUpdateBase, ORMBaseModel):
    id: int
    commission_id: int
    created_at: datetime


class CustomerProgressItem(BaseModel):
    id: int
    message: str
    created_at: datetime
    image_url: Optional[str] = None


class ProductOrderSelectionRead(BaseModel):
    option_name: str
    choice_label: str


class CustomerOrderItem(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_description: Optional[str] = None
    quantity: int
    total_price: Decimal
    status: str
    maker_name: str
    selections: list[ProductOrderSelectionRead]
    created_at: datetime
    updated_at: datetime
    progress_updates: list[CustomerProgressItem]


class CustomerDashboardResponse(BaseModel):
    orders: list[CustomerOrderItem]


class CreateProductOrderSelectionRequest(BaseModel):
    option_id: int
    choice_id: int


class CreateProductOrderRequest(BaseModel):
    quantity: int = Field(default=1, ge=1, le=50)
    selections: list[CreateProductOrderSelectionRequest]


class ProductOrderResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    total_price: Decimal
    status: str
    maker_name: str
    selections: list[ProductOrderSelectionRead]


class WishlistBase(BaseModel):
    customer_id: int
    product_id: int


class WishlistCreate(WishlistBase):
    pass


class WishlistRead(WishlistBase, ORMBaseModel):
    id: int
    created_at: datetime


class WishlistItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_description: Optional[str] = None
    price: Decimal
    maker_id: int
    maker_name: str
    created_at: datetime


class WishlistActionRequest(BaseModel):
    product_id: int = Field(ge=1)


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class CreateProductReviewRequest(ReviewBase):
    pass


class CreateCommissionReviewRequest(ReviewBase):
    pass


class ReviewListItem(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None
    customer_id: int
    customer_name: str
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    commission_id: Optional[int] = None
    commission_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CommissionWithReviewItem(CommissionListItem):
    has_review: bool


class MakerReviewListItem(ReviewListItem):
    target_type: str


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
