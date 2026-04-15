from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Commission,
    MakerProfile,
    Product,
    ProductCustomizationChoice,
    ProductCustomizationOption,
    ProductOrder,
    ProductOrderProgressUpdate,
    ProductOrderSelection,
    Review,
    Wishlist,
    WipUpdate,
    User,
)


COMMISSION_STATUSES = {"pending", "accepted", "rejected", "in_progress", "completed"}


def _base_product_query() -> Select:
    return select(Product).options(
        joinedload(Product.maker).joinedload(User.maker_profile),
        joinedload(Product.customization_options).joinedload(ProductCustomizationOption.choices),
    )


def list_products(
    db: Session,
    *,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    maker_id: int | None = None,
) -> list[Product]:
    statement = _base_product_query().where(Product.is_active.is_(True))

    if min_price is not None:
        statement = statement.where(Product.price >= min_price)

    if max_price is not None:
        statement = statement.where(Product.price <= max_price)

    if maker_id is not None:
        statement = statement.where(Product.maker_id == maker_id)

    statement = statement.order_by(Product.created_at.desc(), Product.id.desc())
    return list(db.scalars(statement).unique().all())


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    statement = _base_product_query().where(
        Product.id == product_id,
        Product.is_active.is_(True),
    )
    return db.scalar(statement)


def get_product_by_id_for_maker(db: Session, product_id: int, maker_id: int) -> Product | None:
    statement = _base_product_query().where(
        Product.id == product_id,
        Product.maker_id == maker_id,
    )
    return db.scalar(statement)


def list_maker_products(db: Session, maker_id: int) -> list[Product]:
    statement = (
        _base_product_query()
        .where(Product.maker_id == maker_id)
        .order_by(Product.created_at.desc(), Product.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def create_maker_product(
    db: Session,
    *,
    maker_id: int,
    title: str,
    description: str | None,
    price: Decimal,
    stock_quantity: int,
    is_active: bool,
) -> Product:
    product = Product(
        maker_id=maker_id,
        title=title.strip(),
        description=description.strip() if description else None,
        price=price,
        stock_quantity=stock_quantity,
        is_active=is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_maker_product(
    db: Session,
    *,
    product: Product,
    title: str,
    description: str | None,
    price: Decimal,
    stock_quantity: int,
    is_active: bool,
) -> Product:
    product.title = title.strip()
    product.description = description.strip() if description else None
    product.price = price
    product.stock_quantity = stock_quantity
    product.is_active = is_active
    db.commit()
    db.refresh(product)
    return product


def delete_maker_product(db: Session, *, product: Product) -> None:
    product.is_active = False
    db.commit()


def get_product_order_overview(db: Session, customer_id: int) -> list[ProductOrder]:
    statement = (
        select(ProductOrder)
        .options(
            joinedload(ProductOrder.product),
            joinedload(ProductOrder.maker).joinedload(User.maker_profile),
            joinedload(ProductOrder.selections).joinedload(ProductOrderSelection.option),
            joinedload(ProductOrder.selections).joinedload(ProductOrderSelection.choice),
            joinedload(ProductOrder.progress_updates),
        )
        .where(ProductOrder.customer_id == customer_id)
        .order_by(ProductOrder.created_at.desc(), ProductOrder.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def create_product_order(
    db: Session,
    *,
    customer_id: int,
    product: Product,
    quantity: int,
    selections: list[tuple[ProductCustomizationOption, ProductCustomizationChoice]],
) -> ProductOrder:
    base_total = Decimal(product.price) * quantity
    total_delta = sum((Decimal(choice.price_delta) for _, choice in selections), Decimal("0.00"))
    total_price = base_total + (total_delta * quantity)

    summary = ", ".join(f"{option.name}: {choice.label}" for option, choice in selections)

    order = ProductOrder(
        product_id=product.id,
        customer_id=customer_id,
        maker_id=product.maker_id,
        quantity=quantity,
        total_price=total_price,
        status="pending",
        customization_summary=summary or None,
    )
    db.add(order)
    db.flush()

    for option, choice in selections:
        db.add(
            ProductOrderSelection(
                order_id=order.id,
                option_id=option.id,
                choice_id=choice.id,
            )
        )

    db.add(
        ProductOrderProgressUpdate(
            order_id=order.id,
            message="Order received. The maker will review your customization choices shortly.",
        )
    )

    db.commit()
    db.refresh(order)
    return order


def get_or_create_maker_profile(db: Session, maker: User) -> MakerProfile:
    profile = db.scalar(select(MakerProfile).where(MakerProfile.user_id == maker.id))
    if profile is not None:
        return profile

    profile = MakerProfile(
        user_id=maker.id,
        shop_name=maker.full_name,
        bio=None,
        specialization=None,
        profile_image_url=None,
        verification_status="unverified",
        contact_email=maker.email,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_maker_profile_by_user_id(db: Session, maker_user_id: int) -> tuple[User, MakerProfile] | None:
    statement = (
        select(User)
        .options(joinedload(User.maker_profile), joinedload(User.role))
        .where(User.id == maker_user_id)
    )
    user = db.scalar(statement)
    if user is None or getattr(user.role, "name", None) != "maker":
        return None

    profile = user.maker_profile or get_or_create_maker_profile(db, user)
    return user, profile


def update_maker_profile(
    db: Session,
    *,
    maker: User,
    shop_name: str,
    bio: str | None,
    specialization: str | None,
    profile_image_url: str | None,
) -> MakerProfile:
    profile = maker.maker_profile or get_or_create_maker_profile(db, maker)
    profile.shop_name = shop_name.strip()
    profile.bio = bio.strip() if bio else None
    profile.specialization = specialization.strip() if specialization else None
    profile.profile_image_url = profile_image_url.strip() if profile_image_url else None
    db.commit()
    db.refresh(profile)
    return profile


def _user_display_name(user: User) -> str:
    maker_profile = getattr(user, "maker_profile", None)
    if maker_profile and maker_profile.shop_name:
        return maker_profile.shop_name
    return user.full_name


def create_commission(
    db: Session,
    *,
    customer_id: int,
    maker: User,
    title: str,
    description: str | None,
    customization_notes: str | None,
    budget: Decimal | None,
) -> Commission:
    commission = Commission(
        customer_id=customer_id,
        maker_id=maker.id,
        title=title.strip(),
        description=description.strip() if description else None,
        customization_notes=customization_notes.strip() if customization_notes else None,
        budget=budget,
        status="pending",
    )
    db.add(commission)
    db.commit()
    db.refresh(commission)
    return commission


def list_customer_commissions(db: Session, customer_id: int) -> list[Commission]:
    statement = (
        select(Commission)
        .options(
            joinedload(Commission.customer),
            joinedload(Commission.maker).joinedload(User.maker_profile),
            joinedload(Commission.wip_updates),
        )
        .where(Commission.customer_id == customer_id)
        .order_by(Commission.created_at.desc(), Commission.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def list_maker_commissions(db: Session, maker_id: int) -> list[Commission]:
    statement = (
        select(Commission)
        .options(
            joinedload(Commission.customer),
            joinedload(Commission.maker).joinedload(User.maker_profile),
            joinedload(Commission.wip_updates),
        )
        .where(Commission.maker_id == maker_id)
        .order_by(Commission.created_at.desc(), Commission.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_maker_user_by_id(db: Session, maker_id: int) -> User | None:
    statement = (
        select(User)
        .options(joinedload(User.role), joinedload(User.maker_profile))
        .where(User.id == maker_id)
    )
    user = db.scalar(statement)
    if user is None or getattr(user.role, "name", None) != "maker":
        return None
    return user


def get_commission_for_maker(db: Session, commission_id: int, maker_id: int) -> Commission | None:
    statement = (
        select(Commission)
        .options(
            joinedload(Commission.customer),
            joinedload(Commission.maker).joinedload(User.maker_profile),
        )
        .where(Commission.id == commission_id, Commission.maker_id == maker_id)
    )
    return db.scalar(statement)


def update_commission_status(db: Session, *, commission: Commission, status: str) -> Commission:
    if status not in COMMISSION_STATUSES:
        raise ValueError("Invalid commission status.")

    commission.status = status
    db.commit()
    db.refresh(commission)
    return commission


def create_wip_update(
    db: Session,
    *,
    commission: Commission,
    message: str,
    image_url: str | None,
) -> WipUpdate:
    update = WipUpdate(
        commission_id=commission.id,
        message=message.strip(),
        image_url=image_url.strip() if image_url else None,
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


def list_user_wishlist(db: Session, customer_id: int) -> list[Wishlist]:
    statement = (
        select(Wishlist)
        .options(joinedload(Wishlist.product).joinedload(Product.maker).joinedload(User.maker_profile))
        .where(Wishlist.customer_id == customer_id)
        .order_by(Wishlist.created_at.desc(), Wishlist.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_wishlist_item(db: Session, customer_id: int, product_id: int) -> Wishlist | None:
    statement = (
        select(Wishlist)
        .options(joinedload(Wishlist.product).joinedload(Product.maker).joinedload(User.maker_profile))
        .where(Wishlist.customer_id == customer_id, Wishlist.product_id == product_id)
    )
    return db.scalar(statement)


def add_to_wishlist(db: Session, *, customer_id: int, product: Product) -> Wishlist:
    existing = get_wishlist_item(db, customer_id, product.id)
    if existing is not None:
        return existing

    wishlist_item = Wishlist(
        customer_id=customer_id,
        product_id=product.id,
    )
    db.add(wishlist_item)
    db.commit()
    return get_wishlist_item(db, customer_id, product.id)


def remove_from_wishlist(db: Session, *, customer_id: int, product_id: int) -> bool:
    wishlist_item = db.scalar(
        select(Wishlist).where(Wishlist.customer_id == customer_id, Wishlist.product_id == product_id)
    )
    if wishlist_item is None:
        return False

    db.delete(wishlist_item)
    db.commit()
    return True


def list_product_reviews(db: Session, product_id: int) -> list[Review]:
    statement = (
        select(Review)
        .options(joinedload(Review.customer), joinedload(Review.product), joinedload(Review.commission))
        .where(Review.product_id == product_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_product_review_by_customer(db: Session, customer_id: int, product_id: int) -> Review | None:
    return db.scalar(
        select(Review).where(Review.customer_id == customer_id, Review.product_id == product_id)
    )


def create_product_review(
    db: Session,
    *,
    customer_id: int,
    product: Product,
    rating: int,
    comment: str | None,
) -> Review:
    existing = get_product_review_by_customer(db, customer_id, product.id)
    if existing is not None:
        raise ValueError("You have already reviewed this product.")

    review = Review(
        customer_id=customer_id,
        product_id=product.id,
        commission_id=None,
        rating=rating,
        comment=comment.strip() if comment else None,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_commission_review_by_customer(db: Session, customer_id: int, commission_id: int) -> Review | None:
    return db.scalar(
        select(Review).where(Review.customer_id == customer_id, Review.commission_id == commission_id)
    )


def get_commission_for_customer(db: Session, commission_id: int, customer_id: int) -> Commission | None:
    statement = (
        select(Commission)
        .options(joinedload(Commission.customer), joinedload(Commission.maker).joinedload(User.maker_profile))
        .where(Commission.id == commission_id, Commission.customer_id == customer_id)
    )
    return db.scalar(statement)


def create_commission_review(
    db: Session,
    *,
    customer_id: int,
    commission: Commission,
    rating: int,
    comment: str | None,
) -> Review:
    if commission.status != "completed":
        raise ValueError("Only completed commissions can be reviewed.")

    existing = get_commission_review_by_customer(db, customer_id, commission.id)
    if existing is not None:
        raise ValueError("You have already reviewed this commission.")

    review = Review(
        customer_id=customer_id,
        product_id=None,
        commission_id=commission.id,
        rating=rating,
        comment=comment.strip() if comment else None,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def list_maker_reviews(db: Session, maker_id: int) -> list[Review]:
    statement = (
        select(Review)
        .options(
            joinedload(Review.customer),
            joinedload(Review.product).joinedload(Product.maker).joinedload(User.maker_profile),
            joinedload(Review.commission).joinedload(Commission.maker).joinedload(User.maker_profile),
        )
        .where(
            (Review.product_id.is_not(None) & Review.product.has(Product.maker_id == maker_id))
            | (Review.commission_id.is_not(None) & Review.commission.has(Commission.maker_id == maker_id))
        )
        .order_by(Review.created_at.desc(), Review.id.desc())
    )
    return list(db.scalars(statement).unique().all())
