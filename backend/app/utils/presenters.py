from app.schemas.marketplace import (
    CommissionListItem,
    CommissionWithReviewItem,
    MakerProfileResponse,
    ProductListItem,
    ProductOrderResponse,
    ProductOrderSelectionRead,
    ReviewListItem,
    WishlistItemResponse,
    WipUpdateRead,
)


def maker_display_name(user) -> str:
    maker_profile = getattr(user, "maker_profile", None)
    if maker_profile and maker_profile.shop_name:
        return maker_profile.shop_name
    return user.full_name


def serialize_wip_update(update) -> WipUpdateRead:
    return WipUpdateRead(
        id=update.id,
        commission_id=update.commission_id,
        message=update.message,
        image_url=update.image_url,
        created_at=update.created_at,
    )


def serialize_product_list_item(product) -> ProductListItem:
    return ProductListItem(
        id=product.id,
        name=product.title,
        description=product.description,
        price=product.price,
        maker_id=product.maker_id,
        maker_name=maker_display_name(product.maker),
    )


def serialize_product_order_response(order) -> ProductOrderResponse:
    return ProductOrderResponse(
        id=order.id,
        product_id=order.product_id,
        product_name=order.product.title,
        quantity=order.quantity,
        total_price=order.total_price,
        status=order.status,
        maker_name=maker_display_name(order.maker),
        selections=[
            ProductOrderSelectionRead(
                option_name=selection.option.name,
                choice_label=selection.choice.label,
            )
            for selection in order.selections
        ],
    )


def serialize_review_item(review) -> ReviewListItem:
    return ReviewListItem(
        id=review.id,
        rating=review.rating,
        comment=review.comment,
        customer_id=review.customer_id,
        customer_name=review.customer.full_name,
        product_id=review.product_id,
        product_name=review.product.title if review.product else None,
        commission_id=review.commission_id,
        commission_title=review.commission.title if review.commission else None,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def serialize_commission_item(commission) -> CommissionListItem:
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
        maker_name=maker_display_name(commission.maker),
        wip_updates=[
            serialize_wip_update(update)
            for update in sorted(
                commission.wip_updates,
                key=lambda item: (item.created_at, item.id),
                reverse=True,
            )
        ],
        created_at=commission.created_at,
        updated_at=commission.updated_at,
    )


def serialize_customer_commission_item(
    commission,
    *,
    has_review: bool,
) -> CommissionWithReviewItem:
    return CommissionWithReviewItem(
        **serialize_commission_item(commission).model_dump(),
        has_review=has_review,
    )


def serialize_wishlist_item(item) -> WishlistItemResponse:
    return WishlistItemResponse(
        id=item.id,
        product_id=item.product_id,
        product_name=item.product.title,
        product_description=item.product.description,
        price=item.product.price,
        maker_id=item.product.maker_id,
        maker_name=maker_display_name(item.product.maker),
        created_at=item.created_at,
    )


def serialize_maker_profile_response(user, profile) -> MakerProfileResponse:
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
