from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.models import (
    Commission,
    MakerProfile,
    Product,
    ProductCustomizationChoice,
    ProductCustomizationOption,
    ProductOrder,
    ProductOrderProgressUpdate,
    ProductOrderSelection,
    Role,
    User,
    Wishlist,
)
from app.services.auth import ensure_system_roles


NEW_MAKER_PRODUCTS = [
    {
        "title": "Custom Name Mug",
        "description": "Handmade ceramic mug with a custom name stamp and warm matte finish.",
        "price": Decimal("22.00"),
        "stock_quantity": 10,
        "options": {
            "Material": [
                {"label": "Stoneware", "price_delta": Decimal("0.00")},
                {"label": "Porcelain", "price_delta": Decimal("4.00")},
            ],
            "Pattern": [
                {"label": "Plain", "price_delta": Decimal("0.00")},
                {"label": "Floral Rim", "price_delta": Decimal("3.00")},
            ],
        },
    },
    {
        "title": "Small Gift Tray",
        "description": "Compact handcrafted tray for jewelry, keys, or a tea set.",
        "price": Decimal("18.50"),
        "stock_quantity": 12,
        "options": {
            "Material": [
                {"label": "Clay", "price_delta": Decimal("0.00")},
                {"label": "Wood", "price_delta": Decimal("5.00")},
            ],
            "Size": [
                {"label": "Small", "price_delta": Decimal("0.00")},
                {"label": "Medium", "price_delta": Decimal("4.50")},
            ],
        },
    },
]


def get_existing_customers(session) -> list[User]:
    return list(
        session.scalars(
            select(User)
            .join(Role, Role.id == User.role_id)
            .where(Role.name == "customer")
            .order_by(User.id)
        ).all()
    )


def get_existing_makers(session) -> list[User]:
    return list(
        session.scalars(
            select(User)
            .join(Role, Role.id == User.role_id)
            .where(Role.name == "maker")
            .order_by(User.id)
        ).all()
    )


def get_or_update_profile(session, maker: User) -> MakerProfile:
    profile = session.scalar(select(MakerProfile).where(MakerProfile.user_id == maker.id))
    if profile is None:
        profile = MakerProfile(
            user_id=maker.id,
            shop_name=maker.full_name,
            bio="Handcrafted items made in small batches.",
            specialization="Custom handmade goods",
            profile_image_url=None,
            verification_status="verified",
            location="Bangkok",
            contact_email=maker.email,
        )
        session.add(profile)
        session.flush()
        return profile

    if not profile.shop_name:
        profile.shop_name = maker.full_name
    profile.bio = profile.bio or "Handcrafted items made in small batches."
    profile.specialization = profile.specialization or "Custom handmade goods"
    profile.verification_status = profile.verification_status or "verified"
    profile.contact_email = profile.contact_email or maker.email
    return profile


def ensure_maker_catalog(session, maker: User) -> int:
    created = 0
    get_or_update_profile(session, maker)

    for product_seed in NEW_MAKER_PRODUCTS:
        product = session.scalar(
            select(Product).where(
                Product.maker_id == maker.id,
                Product.title == product_seed["title"],
            )
        )
        if product is None:
            product = Product(
                maker_id=maker.id,
                title=product_seed["title"],
                description=product_seed["description"],
                price=product_seed["price"],
                stock_quantity=product_seed["stock_quantity"],
                is_active=True,
            )
            session.add(product)
            session.flush()
            created += 1

        for option_name, choices in product_seed["options"].items():
            option = session.scalar(
                select(ProductCustomizationOption).where(
                    ProductCustomizationOption.product_id == product.id,
                    ProductCustomizationOption.name == option_name,
                )
            )
            if option is None:
                option = ProductCustomizationOption(
                    product_id=product.id,
                    name=option_name,
                    is_required=True,
                )
                session.add(option)
                session.flush()

            existing_choice_labels = set(
                session.scalars(
                    select(ProductCustomizationChoice.label).where(
                        ProductCustomizationChoice.option_id == option.id
                    )
                ).all()
            )
            for choice_seed in choices:
                if choice_seed["label"] in existing_choice_labels:
                    continue
                session.add(
                    ProductCustomizationChoice(
                        option_id=option.id,
                        label=choice_seed["label"],
                        price_delta=choice_seed["price_delta"],
                    )
                )

    return created


def ensure_customer_sample_data(session, customer: User, makers: list[User]) -> tuple[int, int, int]:
    created_orders = 0
    created_commissions = 0
    created_wishlist_items = 0

    if session.scalar(select(ProductOrder).where(ProductOrder.customer_id == customer.id)) is None:
        product = session.scalar(select(Product).order_by(Product.id))
        if product is not None:
            order = ProductOrder(
                product_id=product.id,
                customer_id=customer.id,
                maker_id=product.maker_id,
                quantity=1,
                total_price=product.price,
                status="in_progress",
                customization_summary="Sample order for existing user",
            )
            session.add(order)
            session.flush()

            first_option = session.scalar(
                select(ProductCustomizationOption)
                .where(ProductCustomizationOption.product_id == product.id)
                .order_by(ProductCustomizationOption.id)
            )
            if first_option is not None:
                first_choice = session.scalar(
                    select(ProductCustomizationChoice)
                    .where(ProductCustomizationChoice.option_id == first_option.id)
                    .order_by(ProductCustomizationChoice.id)
                )
                if first_choice is not None:
                    session.add(
                        ProductOrderSelection(
                            order_id=order.id,
                            option_id=first_option.id,
                            choice_id=first_choice.id,
                        )
                    )

            session.add_all(
                [
                    ProductOrderProgressUpdate(
                        order_id=order.id,
                        message="Order created for the existing account seed.",
                    ),
                    ProductOrderProgressUpdate(
                        order_id=order.id,
                        message="Maker is preparing materials for this order.",
                    ),
                ]
            )
            created_orders += 1

    if session.scalar(select(Commission).where(Commission.customer_id == customer.id)) is None and makers:
        maker = makers[0]
        session.add(
            Commission(
                customer_id=customer.id,
                maker_id=maker.id,
                title="Custom gift request",
                description="Sample commission added for an existing customer account.",
                customization_notes="Please keep the tone warm and simple.",
                budget=Decimal("55.00"),
                status="accepted",
            )
        )
        created_commissions += 1

    if session.scalar(select(Wishlist).where(Wishlist.customer_id == customer.id)) is None:
        wishlist_product = session.scalar(
            select(Product)
            .where(Product.is_active.is_(True))
            .order_by(Product.id.desc())
        )
        if wishlist_product is not None:
            session.add(Wishlist(customer_id=customer.id, product_id=wishlist_product.id))
            created_wishlist_items += 1

    return created_orders, created_commissions, created_wishlist_items


def seed_existing_users() -> None:
    init_db()

    with SessionLocal() as session:
        ensure_system_roles(session)

        makers = get_existing_makers(session)
        customers = get_existing_customers(session)

        created_products = 0
        created_orders = 0
        created_commissions = 0
        created_wishlist_items = 0

        for maker in makers:
            existing_products = session.scalar(
                select(Product.id).where(Product.maker_id == maker.id)
            )
            if existing_products is None:
                created_products += ensure_maker_catalog(session, maker)
            else:
                get_or_update_profile(session, maker)

        session.commit()
        makers = get_existing_makers(session)

        for customer in customers:
            order_count, commission_count, wishlist_count = ensure_customer_sample_data(
                session,
                customer,
                makers,
            )
            created_orders += order_count
            created_commissions += commission_count
            created_wishlist_items += wishlist_count

        session.commit()
        print(f"Created {created_products} new products for existing maker accounts.")
        print(f"Created {created_orders} new orders for existing customer accounts.")
        print(f"Created {created_commissions} new commissions for existing customer accounts.")
        print(f"Created {created_wishlist_items} wishlist items for existing customer accounts.")


if __name__ == "__main__":
    seed_existing_users()
