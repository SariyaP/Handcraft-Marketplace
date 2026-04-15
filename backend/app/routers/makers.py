from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.marketplace import MakerProfileResponse, MakerProfileUpdateRequest
from app.services.marketplace import (
    get_maker_profile_by_user_id,
    get_or_create_maker_profile,
    update_maker_profile,
)
from app.utils.dependencies import require_roles


router = APIRouter(tags=["makers"])


def _serialize_maker_profile(user, profile) -> MakerProfileResponse:
    return MakerProfileResponse(
        id=profile.id,
        user_id=user.id,
        full_name=user.full_name,
        shop_name=profile.shop_name,
        bio=profile.bio,
        specialization=profile.specialization,
        profile_image_url=profile.profile_image_url,
        verification_status=profile.verification_status,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get(
    "/maker/profile",
    response_model=MakerProfileResponse,
    summary="Get the authenticated maker profile",
)
def read_own_maker_profile(
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> MakerProfileResponse:
    profile = user.maker_profile or get_or_create_maker_profile(db, user)
    return _serialize_maker_profile(user, profile)


@router.put(
    "/maker/profile",
    response_model=MakerProfileResponse,
    summary="Update the authenticated maker profile",
)
def update_own_maker_profile(
    payload: MakerProfileUpdateRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("maker")),
) -> MakerProfileResponse:
    profile = update_maker_profile(
        db,
        maker=user,
        shop_name=payload.shop_name,
        bio=payload.bio,
        specialization=payload.specialization,
        profile_image_url=payload.profile_image_url,
    )
    return _serialize_maker_profile(user, profile)


@router.get(
    "/makers/{maker_user_id}",
    response_model=MakerProfileResponse,
    summary="Get a public maker profile by maker user id",
)
def read_public_maker_profile(
    maker_user_id: int,
    db: Session = Depends(get_db),
) -> MakerProfileResponse:
    result = get_maker_profile_by_user_id(db, maker_user_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maker profile not found.",
        )

    user, profile = result
    return _serialize_maker_profile(user, profile)
