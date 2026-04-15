from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.marketplace import (
    CommissionListItem,
    CommissionWithReviewItem,
    CreateCommissionRequest,
    WipUpdateCreate,
    WipUpdateRead,
    UpdateCommissionStatusRequest,
)
from app.services.marketplace import (
    create_wip_update,
    create_commission,
    get_commission_review_by_customer,
    get_commission_for_maker,
    get_maker_user_by_id,
    list_customer_commissions,
    list_maker_commissions,
    update_commission_status,
)
from app.utils.dependencies import require_roles
from app.utils.presenters import (
    serialize_commission_item,
    serialize_customer_commission_item,
    serialize_wip_update,
)


router = APIRouter(tags=["commissions"])

@router.post(
    "/commissions",
    response_model=CommissionListItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a commission request",
)
def create_commission_request(
    payload: CreateCommissionRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> CommissionListItem:
    maker = get_maker_user_by_id(db, payload.maker_id)
    if maker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maker not found.",
        )

    commission = create_commission(
        db,
        customer_id=user.id,
        maker=maker,
        title=payload.title,
        description=payload.description,
        customization_notes=payload.customization_notes,
        budget=payload.budget,
    )

    commission.customer = user
    commission.maker = maker
    return serialize_commission_item(commission)


@router.get(
    "/commissions",
    response_model=list[CommissionWithReviewItem],
    summary="List commissions for the authenticated customer",
)
def read_customer_commissions(
    db: Session = Depends(get_db),
    user=Depends(require_roles("customer")),
) -> list[CommissionWithReviewItem]:
    commissions = list_customer_commissions(db, user.id)
    return [
        serialize_customer_commission_item(
            commission,
            has_review=get_commission_review_by_customer(db, user.id, commission.id) is not None,
        )
        for commission in commissions
    ]


@router.get(
    "/maker/commissions",
    response_model=list[CommissionListItem],
    summary="List incoming commissions for the authenticated maker",
)
def read_maker_commissions(
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> list[CommissionListItem]:
    commissions = list_maker_commissions(db, user.id)
    return [serialize_commission_item(commission) for commission in commissions]


@router.put(
    "/commissions/{commission_id}",
    response_model=CommissionListItem,
    summary="Update commission status as the assigned maker",
)
def update_maker_commission(
    commission_id: int,
    payload: UpdateCommissionStatusRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> CommissionListItem:
    commission = get_commission_for_maker(db, commission_id, user.id)
    if commission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission not found.",
        )

    try:
        updated = update_commission_status(db, commission=commission, status=payload.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return serialize_commission_item(updated)


@router.post(
    "/commissions/{commission_id}/updates",
    response_model=WipUpdateRead,
    status_code=status.HTTP_201_CREATED,
    summary="Post a WIP update for a commission as the assigned maker",
)
def create_commission_wip_update(
    commission_id: int,
    payload: WipUpdateCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> WipUpdateRead:
    commission = get_commission_for_maker(db, commission_id, user.id)
    if commission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Commission not found.",
        )

    update = create_wip_update(
        db,
        commission=commission,
        message=payload.message,
        image_url=payload.image_url,
    )
    return serialize_wip_update(update)
