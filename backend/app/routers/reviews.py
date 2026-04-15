from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.marketplace import (
    CreateCommissionReviewRequest,
    CreateProductReviewRequest,
    MakerReviewListItem,
    ReviewListItem,
)
from app.services.marketplace import (
    create_commission_review,
    create_product_review,
    get_commission_for_customer,
    get_product_by_id,
    list_maker_reviews,
    list_product_reviews,
)
from app.utils.dependencies import require_roles
from app.utils.presenters import serialize_review_item


router = APIRouter(tags=["reviews"])

@router.get(
    "/products/{product_id}/reviews",
    response_model=list[ReviewListItem],
    summary="List reviews for a product",
)
def read_product_reviews(product_id: int, db: Session = Depends(get_db)) -> list[ReviewListItem]:
    reviews = list_product_reviews(db, product_id)
    return [serialize_review_item(review) for review in reviews]


@router.post(
    "/products/{product_id}/reviews",
    response_model=ReviewListItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product review",
)
def create_review_for_product(
    product_id: int,
    payload: CreateProductReviewRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> ReviewListItem:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    try:
        review = create_product_review(
            db,
            customer_id=user.id,
            product=product,
            rating=payload.rating,
            comment=payload.comment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    review.customer = user
    review.product = product
    return serialize_review_item(review)


@router.post(
    "/commissions/{commission_id}/reviews",
    response_model=ReviewListItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a completed commission review",
)
def create_review_for_commission(
    commission_id: int,
    payload: CreateCommissionReviewRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> ReviewListItem:
    commission = get_commission_for_customer(db, commission_id, user.id)
    if commission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission not found.",
        )

    try:
        review = create_commission_review(
            db,
            customer_id=user.id,
            commission=commission,
            rating=payload.rating,
            comment=payload.comment,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = (
            status.HTTP_422_UNPROCESSABLE_ENTITY
            if "completed commissions" in detail
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code=status_code, detail=detail) from exc

    review.customer = user
    review.commission = commission
    return serialize_review_item(review)


@router.get(
    "/maker/reviews",
    response_model=list[MakerReviewListItem],
    summary="List reviews for the authenticated maker",
)
def read_maker_reviews(
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> list[MakerReviewListItem]:
    reviews = list_maker_reviews(db, user.id)
    return [
        MakerReviewListItem(
            **serialize_review_item(review).model_dump(),
            target_type="product" if review.product_id is not None else "commission",
        )
        for review in reviews
    ]
