from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.marketplace import (
    CreateProductOrderRequest,
    MakerProductCreateRequest,
    MakerProductResponse,
    MakerProductUpdateRequest,
    ProductCustomizationOptionRead,
    ProductCustomizationChoiceRead,
    ProductDetailResponse,
    ProductListItem,
    ProductOrderResponse,
    ProductOrderSelectionRead,
    ReviewListItem,
)
from app.services.marketplace import (
    create_maker_product,
    create_product_order,
    delete_maker_product,
    get_product_by_id,
    get_product_by_id_for_maker,
    list_product_reviews,
    list_maker_products,
    list_products,
    update_maker_product,
)
from app.utils.dependencies import require_roles


router = APIRouter(prefix="/products", tags=["products"])
maker_router = APIRouter(prefix="/maker", tags=["maker-products"])


def _maker_name_for_product(product) -> str:
    maker_profile = getattr(product.maker, "maker_profile", None)
    if maker_profile and maker_profile.shop_name:
        return maker_profile.shop_name

    return product.maker.full_name


def _serialize_product(product) -> ProductListItem:
    return ProductListItem(
        id=product.id,
        name=product.title,
        description=product.description,
        price=product.price,
        maker_id=product.maker_id,
        maker_name=_maker_name_for_product(product),
    )


def _serialize_order(order) -> ProductOrderResponse:
    maker_profile = getattr(order.maker, "maker_profile", None)
    maker_name = maker_profile.shop_name if maker_profile and maker_profile.shop_name else order.maker.full_name
    return ProductOrderResponse(
        id=order.id,
        product_id=order.product_id,
        product_name=order.product.title,
        quantity=order.quantity,
        total_price=order.total_price,
        status=order.status,
        maker_name=maker_name,
        selections=[
            ProductOrderSelectionRead(
                option_name=selection.option.name,
                choice_label=selection.choice.label,
            )
            for selection in order.selections
        ],
    )


def _serialize_maker_product(product) -> MakerProductResponse:
    return MakerProductResponse(
        id=product.id,
        title=product.title,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.get("", response_model=list[ProductListItem], summary="List products")
def read_products(
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    maker_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
) -> list[ProductListItem]:
    products = list_products(
        db,
        min_price=min_price,
        max_price=max_price,
        maker_id=maker_id,
    )
    return [_serialize_product(product) for product in products]


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Get product details",
)
def read_product(product_id: int, db: Session = Depends(get_db)) -> ProductDetailResponse:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return ProductDetailResponse(
        **_serialize_product(product).model_dump(),
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
        customization_options=[
            ProductCustomizationOptionRead(
                id=option.id,
                name=option.name,
                is_required=option.is_required,
                choices=[
                    ProductCustomizationChoiceRead(
                        id=choice.id,
                        label=choice.label,
                        price_delta=choice.price_delta,
                    )
                    for choice in option.choices
                ],
            )
            for option in product.customization_options
        ],
        reviews=[
            ReviewListItem(
                id=review.id,
                rating=review.rating,
                comment=review.comment,
                customer_id=review.customer_id,
                customer_name=review.customer.full_name,
                product_id=review.product_id,
                product_name=product.title,
                commission_id=review.commission_id,
                commission_title=review.commission.title if review.commission else None,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review in list_product_reviews(db, product.id)
        ],
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.post(
    "/{product_id}/orders",
    response_model=ProductOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a configured product order",
)
def create_order_for_product(
    product_id: int,
    payload: CreateProductOrderRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> ProductOrderResponse:
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    selections_by_option_id = {selection.option_id: selection.choice_id for selection in payload.selections}
    resolved_selections = []

    for option in product.customization_options:
        selected_choice_id = selections_by_option_id.get(option.id)
        if option.is_required and selected_choice_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Please choose a value for {option.name}.",
            )
        if selected_choice_id is None:
            continue

        choice = next((item for item in option.choices if item.id == selected_choice_id), None)
        if choice is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid choice selected for {option.name}.",
            )
        resolved_selections.append((option, choice))

    order = create_product_order(
        db,
        customer_id=user.id,
        product=product,
        quantity=payload.quantity,
        selections=resolved_selections,
    )
    return _serialize_order(order)


@router.post(
    "",
    response_model=MakerProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product for the authenticated maker",
)
def create_product(
    payload: MakerProductCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> MakerProductResponse:
    product = create_maker_product(
        db,
        maker_id=user.id,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
        is_active=payload.is_active,
    )
    return _serialize_maker_product(product)


@maker_router.get(
    "/products",
    response_model=list[MakerProductResponse],
    summary="List products owned by the authenticated maker",
)
def read_maker_products(
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> list[MakerProductResponse]:
    products = list_maker_products(db, user.id)
    return [_serialize_maker_product(product) for product in products]


@router.put(
    "/{product_id}",
    response_model=MakerProductResponse,
    summary="Update a product owned by the authenticated maker",
)
def update_product(
    product_id: int,
    payload: MakerProductUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> MakerProductResponse:
    product = get_product_by_id_for_maker(db, product_id, user.id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    updated_product = update_maker_product(
        db,
        product=product,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
        is_active=payload.is_active,
    )
    return _serialize_maker_product(updated_product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product owned by the authenticated maker",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> Response:
    product = get_product_by_id_for_maker(db, product_id, user.id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    delete_maker_product(db, product=product)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
