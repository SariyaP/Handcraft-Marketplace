from __future__ import annotations

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


router = APIRouter(tags=["commissions"])


def _maker_display_name(user) -> str:
    maker_profile = getattr(user, "maker_profile", None)
    if maker_profile and maker_profile.shop_name:
        return maker_profile.shop_name
    return user.full_name


def _serialize_commission(commission) -> CommissionListItem:
    return CommissionListItem(
        id=commission.id,
        title=commission.title,
        description=commission.description,
        customization_notes=commission.customization_notes,
        budget=commission.budget,
        status=commission.status,
        customer_id=commission.customer_id,
        customer_name=commission.customer.full_name,
        maker_id=commission.maker_id,
        maker_name=_maker_display_name(commission.maker),
        wip_updates=[
            WipUpdateRead(
                id=update.id,
                commission_id=update.commission_id,
                message=update.message,
                image_url=update.image_url,
                created_at=update.created_at,
            )
            for update in sorted(
                commission.wip_updates,
                key=lambda item: (item.created_at, item.id),
                reverse=True,
            )
        ],
        created_at=commission.created_at,
        updated_at=commission.updated_at,
    )


def _serialize_customer_commission(commission, has_review: bool) -> CommissionWithReviewItem:
    return CommissionWithReviewItem(
        **_serialize_commission(commission).model_dump(),
        has_review=has_review,
    )


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
    return _serialize_commission(commission)


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
        _serialize_customer_commission(
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
    return [_serialize_commission(commission) for commission in commissions]


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

    return _serialize_commission(updated)


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
    return WipUpdateRead(
        id=update.id,
        commission_id=update.commission_id,
        message=update.message,
        image_url=update.image_url,
        created_at=update.created_at,
    )
