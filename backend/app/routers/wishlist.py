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
from app.utils.presenters import serialize_wishlist_item


router = APIRouter(tags=["wishlist"])

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
    return [serialize_wishlist_item(item) for item in items]


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
    return serialize_wishlist_item(item)


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
