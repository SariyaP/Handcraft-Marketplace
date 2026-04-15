from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.marketplace import WishlistActionRequest, WishlistItemResponse
from app.services.marketplace import (
    add_to_wishlist,
    get_product_by_id,
    list_user_wishlist,
    remove_from_wishlist,
)
from app.utils.dependencies import require_roles


router = APIRouter(tags=["wishlist"])


def _maker_name_for_product(product) -> str:
    maker_profile = getattr(product.maker, "maker_profile", None)
    if maker_profile and maker_profile.shop_name:
        return maker_profile.shop_name
    return product.maker.full_name


def _serialize_wishlist_item(item) -> WishlistItemResponse:
    return WishlistItemResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=item.product.title,
        product_description=item.product.description,
        price=item.product.price,
        maker_id=item.product.maker_id,
        maker_name=_maker_name_for_product(item.product),
        created_at=item.created_at,
    )


@router.get(
    "/wishlist",
    response_model=list[WishlistItemResponse],
    summary="List wishlist items for the authenticated customer",
)
def read_wishlist(
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> list[WishlistItemResponse]:
    items = list_user_wishlist(db, user.id)
    return [_serialize_wishlist_item(item) for item in items]


@router.post(
    "/wishlist",
    response_model=WishlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a product to the authenticated customer's wishlist",
)
def create_wishlist_item(
    payload: WishlistActionRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> WishlistItemResponse:
    product = get_product_by_id(db, payload.product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    item = add_to_wishlist(db, customer_id=user.id, product=product)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create wishlist item.",
        )
    return _serialize_wishlist_item(item)


@router.delete(
    "/wishlist/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a product from the authenticated customer's wishlist",
)
def delete_wishlist_item(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> Response:
    removed = remove_from_wishlist(db, customer_id=user.id, product_id=product_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
