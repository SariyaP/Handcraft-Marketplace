from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import MakerProfile, Product, Review, ShopVerification, User


def list_admin_users(db: Session) -> list[User]:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .order_by(User.created_at.desc(), User.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def list_admin_products(db: Session) -> list[Product]:
    statement = (
        select(Product)
        .options(joinedload(Product.maker).joinedload(User.maker_profile))
        .order_by(Product.created_at.desc(), Product.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_product_for_admin(db: Session, product_id: int) -> Product | None:
    statement = (
        select(Product)
        .options(joinedload(Product.maker).joinedload(User.maker_profile))
        .where(Product.id == product_id)
    )
    return db.scalar(statement)


def moderate_product(db: Session, product: Product) -> None:
    product.is_active = False
    db.commit()


def list_admin_verifications(db: Session) -> list[tuple[User, MakerProfile | None, ShopVerification | None]]:
    makers = list(
        db.scalars(
            select(User)
            .options(
                joinedload(User.role),
                joinedload(User.maker_profile),
                joinedload(User.shop_verifications),
            )
            .order_by(User.created_at.desc(), User.id.desc())
        )
        .unique()
        .all()
    )

    maker_rows: list[tuple[User, MakerProfile | None, ShopVerification | None]] = []
    for maker in makers:
        if getattr(maker.role, "name", None) != "maker":
            continue

        latest_verification = None
        if maker.shop_verifications:
            latest_verification = max(maker.shop_verifications, key=lambda item: item.updated_at)

        maker_rows.append((maker, maker.maker_profile, latest_verification))

    return maker_rows


def get_maker_for_admin(db: Session, maker_id: int) -> User | None:
    statement = (
        select(User)
        .options(
            joinedload(User.role),
            joinedload(User.maker_profile),
            joinedload(User.shop_verifications),
        )
        .where(User.id == maker_id)
    )
    user = db.scalar(statement)
    if user is None or getattr(user.role, "name", None) != "maker":
        return None
    return user


def update_shop_verification(
    db: Session,
    *,
    maker: User,
    status: str,
    notes: str | None,
) -> ShopVerification:
    profile = maker.maker_profile
    if profile is None:
        profile = MakerProfile(
            user_id=maker.id,
            shop_name=maker.full_name,
            contact_email=maker.email,
            verification_status=status,
        )
        db.add(profile)
        db.flush()

    profile.verification_status = status

    verification = None
    if maker.shop_verifications:
        verification = max(maker.shop_verifications, key=lambda item: item.updated_at)

    if verification is None:
        verification = ShopVerification(
            maker_id=maker.id,
            document_url=None,
            status=status,
            notes=notes.strip() if notes else None,
        )
        db.add(verification)
    else:
        verification.status = status
        verification.notes = notes.strip() if notes else None

    db.commit()
    db.refresh(verification)
    return verification


def list_admin_reviews(db: Session) -> list[Review]:
    statement = (
        select(Review)
        .options(
            joinedload(Review.customer),
            joinedload(Review.product),
            joinedload(Review.commission),
        )
        .order_by(Review.created_at.desc(), Review.id.desc())
    )
    return list(db.scalars(statement).unique().all())


def update_user_status(db: Session, *, user: User, is_active: bool) -> User:
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def get_review_for_admin(db: Session, review_id: int) -> Review | None:
    statement = (
        select(Review)
        .options(
            joinedload(Review.customer),
            joinedload(Review.product),
            joinedload(Review.commission),
        )
        .where(Review.id == review_id)
    )
    return db.scalar(statement)


def delete_review_for_admin(db: Session, review: Review) -> None:
    db.delete(review)
    db.commit()
