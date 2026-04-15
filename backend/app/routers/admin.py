from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.admin import (
    AdminProductListItem,
    AdminReviewListItem,
    AdminUserListItem,
    AdminVerificationListItem,
    UpdateUserStatusRequest,
    UpdateVerificationRequest,
)
from app.services.admin import (
    delete_review_for_admin,
    get_maker_for_admin,
    get_product_for_admin,
    get_review_for_admin,
    list_admin_products,
    list_admin_reviews,
    list_admin_users,
    list_admin_verifications,
    moderate_product,
    update_user_status,
    update_shop_verification,
)
from app.services.auth import get_user_by_id
from app.utils.dependencies import require_roles


router = APIRouter(tags=["admin"])


def _maker_display_name(user) -> str:
    maker_profile = getattr(user, "maker_profile", None)
    if maker_profile and maker_profile.shop_name:
        return maker_profile.shop_name
    return user.full_name


@router.get(
    "/admin/users",
    response_model=list[AdminUserListItem],
    summary="List all users for admin moderation",
)
def read_admin_users(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[AdminUserListItem]:
    users = list_admin_users(db)
    return [
        AdminUserListItem(
            id=item.id,
            email=item.email,
            full_name=item.full_name,
            role=item.role.name,
            is_active=item.is_active,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in users
    ]


@router.put(
    "/admin/users/{user_id}",
    response_model=AdminUserListItem,
    summary="Update a user's active status as admin",
)
def update_admin_user(
    user_id: int,
    payload: UpdateUserStatusRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AdminUserListItem:
    managed_user = get_user_by_id(db, user_id)
    if managed_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if managed_user.id == user.id and payload.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Admins cannot deactivate their own account.",
        )

    updated_user = update_user_status(db, user=managed_user, is_active=payload.is_active)
    return AdminUserListItem(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role.name,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


@router.get(
    "/admin/products",
    response_model=list[AdminProductListItem],
    summary="List all products for admin moderation",
)
def read_admin_products(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[AdminProductListItem]:
    products = list_admin_products(db)
    return [
        AdminProductListItem(
            id=item.id,
            title=item.title,
            description=item.description,
            price=float(item.price),
            stock_quantity=item.stock_quantity,
            is_active=item.is_active,
            maker_id=item.maker_id,
            maker_name=_maker_display_name(item.maker),
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in products
    ]


@router.delete(
    "/admin/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Remove a product from public listing",
)
def remove_admin_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> Response:
    product = get_product_for_admin(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    moderate_product(db, product)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/admin/verifications",
    response_model=list[AdminVerificationListItem],
    summary="List maker shop verifications",
)
def read_admin_verifications(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[AdminVerificationListItem]:
    items = list_admin_verifications(db)
    results: list[AdminVerificationListItem] = []

    for maker, profile, verification in items:
        results.append(
            AdminVerificationListItem(
                maker_id=maker.id,
                maker_name=maker.full_name,
                shop_name=profile.shop_name if profile else None,
                contact_email=(profile.contact_email if profile else maker.email),
                profile_verification_status=(
                    profile.verification_status if profile else "unverified"
                ),
                document_url=verification.document_url if verification else None,
                status=verification.status if verification else "pending",
                notes=verification.notes if verification else None,
                created_at=(
                    verification.created_at
                    if verification
                    else (profile.created_at if profile else maker.created_at)
                ),
                updated_at=(
                    verification.updated_at
                    if verification
                    else (profile.updated_at if profile else maker.updated_at)
                ),
            )
        )

    return results


@router.put(
    "/admin/verifications/{maker_id}",
    response_model=AdminVerificationListItem,
    summary="Update maker verification status",
)
def update_admin_verification(
    maker_id: int,
    payload: UpdateVerificationRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AdminVerificationListItem:
    maker = get_maker_for_admin(db, maker_id)
    if maker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maker not found.")

    verification = update_shop_verification(
        db,
        maker=maker,
        status=payload.status,
        notes=payload.notes,
    )
    profile = maker.maker_profile

    return AdminVerificationListItem(
        maker_id=maker.id,
        maker_name=maker.full_name,
        shop_name=profile.shop_name if profile else None,
        contact_email=(profile.contact_email if profile else maker.email),
        profile_verification_status=profile.verification_status if profile else payload.status,
        document_url=verification.document_url,
        status=verification.status,
        notes=verification.notes,
        created_at=verification.created_at,
        updated_at=verification.updated_at,
    )


@router.get(
    "/admin/reviews",
    response_model=list[AdminReviewListItem],
    summary="List all reviews for admin moderation",
)
def read_admin_reviews(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[AdminReviewListItem]:
    reviews = list_admin_reviews(db)
    return [
        AdminReviewListItem(
            id=item.id,
            rating=item.rating,
            comment=item.comment,
            customer_id=item.customer_id,
            customer_name=item.customer.full_name,
            target_type="product" if item.product_id is not None else "commission",
            target_id=item.product_id or item.commission_id,
            target_name=(
                item.product.title
                if item.product is not None
                else item.commission.title
            ),
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in reviews
    ]


@router.delete(
    "/admin/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Remove a review as admin",
)
def remove_admin_review(
    review_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> Response:
    review = get_review_for_admin(db, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

    delete_review_for_admin(db, review)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
