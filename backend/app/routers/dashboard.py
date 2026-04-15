from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas.marketplace import (
    CustomerDashboardResponse,
    CustomerOrderItem,
    CustomerProgressItem,
    ProductOrderSelectionRead,
)
from app.services.marketplace import get_product_order_overview
from app.utils.dependencies import require_roles


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/customer", summary="Customer-only dashboard endpoint")
def read_customer_dashboard(user=Depends(require_roles("customer"))):
    return {
        "message": f"Welcome to the customer dashboard, {user.full_name}.",
        "role": user.role.name,
    }


@router.get(
    "/customer/overview",
    response_model=CustomerDashboardResponse,
    summary="Customer dashboard overview",
)
def read_customer_overview(
    user=Depends(require_roles("customer")),
    db=Depends(get_db),
):
    orders = get_product_order_overview(db, user.id)

    serialized_orders = []
    for order in orders:
        maker_profile = getattr(order.maker, "maker_profile", None)
        maker_name = (
            maker_profile.shop_name
            if maker_profile and maker_profile.shop_name
            else order.maker.full_name
        )
        updates = sorted(
            order.progress_updates,
            key=lambda item: (item.created_at, item.id),
            reverse=True,
        )
        serialized_orders.append(
            CustomerOrderItem(
                id=order.id,
                product_id=order.product_id,
                product_name=order.product.title,
                product_description=order.product.description,
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
                created_at=order.created_at,
                updated_at=order.updated_at,
                progress_updates=[
                    CustomerProgressItem(
                        id=update.id,
                        message=update.message,
                        created_at=update.created_at,
                        image_url=update.image_url,
                    )
                    for update in updates
                ],
            )
        )

    return CustomerDashboardResponse(orders=serialized_orders)


@router.get("/maker", summary="Maker-only dashboard endpoint")
def read_maker_dashboard(user=Depends(require_roles("maker"))):
    return {
        "message": f"Welcome to the maker dashboard, {user.full_name}.",
        "role": user.role.name,
    }


@router.get("/admin", summary="Admin-only dashboard endpoint")
def read_admin_dashboard(user=Depends(require_roles("admin"))):
    return {
        "message": f"Welcome to the admin dashboard, {user.full_name}.",
        "role": user.role.name,
    }
