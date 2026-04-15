from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class AdminUserListItem(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdminProductListItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    is_active: bool
    maker_id: int
    maker_name: str
    created_at: datetime
    updated_at: datetime


class AdminVerificationListItem(BaseModel):
    maker_id: int
    maker_name: str
    shop_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    profile_verification_status: str
    document_url: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UpdateVerificationRequest(BaseModel):
    status: str = Field(pattern="^(pending|verified|rejected)$")
    notes: Optional[str] = None


class UpdateUserStatusRequest(BaseModel):
    is_active: bool


class AdminReviewListItem(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None
    customer_id: int
    customer_name: str
    target_type: str
    target_id: int
    target_name: str
    created_at: datetime
    updated_at: datetime
