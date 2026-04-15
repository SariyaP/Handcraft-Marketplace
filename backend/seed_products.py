from __future__ import annotations

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
)
from app.services.auth import ensure_system_roles
from app.utils.security import hash_password


SEED_MAKERS = [
    {
        "email": "lila.ceramics@example.com",
        "full_name": "Lila Ceramics",
        "shop_name": "Clay Song Studio",
        "bio": "Wheel-thrown tableware and small-batch ceramic home pieces.",
        "specialization": "Ceramics and tableware",
        "profile_image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=80",
        "location": "Chiang Mai",
        "products": [
            {
                "title": "Speckled Tea Cup Set",
                "description": "A set of two hand-thrown tea cups with a warm speckled glaze.",
                "price": Decimal("24.00"),
                "stock_quantity": 12,
                "options": {
                    "Material": [
                        {"label": "Stoneware", "price_delta": Decimal("0.00")},
                        {"label": "Porcelain", "price_delta": Decimal("4.00")},
                    ],
                    "Pattern": [
                        {"label": "Speckled Sand", "price_delta": Decimal("0.00")},
                        {"label": "Forest Brushstroke", "price_delta": Decimal("3.50")},
                    ],
                },
            },
            {
                "title": "Stoneware Serving Bowl",
                "description": "Large serving bowl with a satin white glaze and trimmed foot.",
                "price": Decimal("38.50"),
                "stock_quantity": 6,
                "options": {
                    "Size": [
                        {"label": "Medium", "price_delta": Decimal("0.00")},
                        {"label": "Large", "price_delta": Decimal("7.50")},
                    ],
                    "Glaze": [
                        {"label": "Warm White", "price_delta": Decimal("0.00")},
                        {"label": "Ash Blue", "price_delta": Decimal("2.50")},
                    ],
                },
            },
        ],
    },
    {
        "email": "niran.weave@example.com",
        "full_name": "Niran Weave",
        "shop_name": "River Loom",
        "bio": "Textile maker focused on handwoven scarves and home linens.",
        "specialization": "Textiles and woven accessories",
        "profile_image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80",
        "location": "Bangkok",
        "products": [
            {
                "title": "Indigo Loom Scarf",
                "description": "Soft handwoven cotton scarf dyed in layered indigo tones.",
                "price": Decimal("31.00"),
                "stock_quantity": 10,
                "options": {
                    "Material": [
                        {"label": "Cotton", "price_delta": Decimal("0.00")},
                        {"label": "Cotton-Linen Blend", "price_delta": Decimal("5.00")},
                    ],
                    "Length": [
                        {"label": "Standard", "price_delta": Decimal("0.00")},
                        {"label": "Long", "price_delta": Decimal("6.00")},
                    ],
                },
            },
            {
                "title": "Natural Fiber Table Runner",
                "description": "Textured woven table runner made from a linen-cotton blend.",
                "price": Decimal("28.75"),
                "stock_quantity": 8,
                "options": {
                    "Pattern": [
                        {"label": "Plain Weave", "price_delta": Decimal("0.00")},
                        {"label": "Striped Border", "price_delta": Decimal("3.00")},
                    ],
                    "Length": [
                        {"label": "120 cm", "price_delta": Decimal("0.00")},
                        {"label": "160 cm", "price_delta": Decimal("5.50")},
                    ],
                },
            },
        ],
    },
    {
        "email": "mara.wood@example.com",
        "full_name": "Mara Wood",
        "shop_name": "North Grain Workshop",
        "bio": "Small wooden kitchenware and carved decorative objects.",
        "specialization": "Woodworking and kitchen tools",
        "profile_image_url": "https://images.unsplash.com/photo-1517705008128-361805f42e86?auto=format&fit=crop&w=900&q=80",
        "location": "Pai",
        "products": [
            {
                "title": "Carved Walnut Spoon",
                "description": "Hand-carved walnut cooking spoon finished with food-safe oil.",
                "price": Decimal("18.00"),
                "stock_quantity": 15,
                "options": {
                    "Wood": [
                        {"label": "Walnut", "price_delta": Decimal("0.00")},
                        {"label": "Cherry", "price_delta": Decimal("2.00")},
                    ],
                    "Handle Style": [
                        {"label": "Classic", "price_delta": Decimal("0.00")},
                        {"label": "Tapered", "price_delta": Decimal("1.50")},
                    ],
                },
            },
            {
                "title": "Ash Wood Serving Board",
                "description": "Minimal serving board with rounded edges and hanging loop.",
                "price": Decimal("42.00"),
                "stock_quantity": 5,
                "options": {
                    "Size": [
                        {"label": "Small", "price_delta": Decimal("0.00")},
                        {"label": "Large", "price_delta": Decimal("8.00")},
                    ],
                    "Pattern": [
                        {"label": "Natural Grain", "price_delta": Decimal("0.00")},
                        {"label": "Geometric Burn Finish", "price_delta": Decimal("6.50")},
                    ],
                },
            },
        ],
    },
]

SEED_CUSTOMER = {
    "email": "mina.customer@example.com",
    "full_name": "Mina Customer",
}


def get_or_create_maker_role(session) -> Role:
    role = session.scalar(select(Role).where(Role.name == "maker"))
    if role is None:
        raise RuntimeError("Maker role is missing after role initialization.")
    return role


def get_or_create_maker_user(session, maker_role: Role, maker_seed: dict) -> User:
    user = session.scalar(select(User).where(User.email == maker_seed["email"]))
    if user is not None:
        return user

    user = User(
        email=maker_seed["email"],
        full_name=maker_seed["full_name"],
        password_hash=hash_password("password123"),
        role=maker_role,
        is_active=True,
    )
    session.add(user)
    session.flush()
    return user


def get_or_create_maker_profile(session, user: User, maker_seed: dict) -> None:
    profile = session.scalar(select(MakerProfile).where(MakerProfile.user_id == user.id))
    if profile is not None:
        return

    session.add(
        MakerProfile(
            user_id=user.id,
            shop_name=maker_seed["shop_name"],
            bio=maker_seed["bio"],
            specialization=maker_seed["specialization"],
            profile_image_url=maker_seed["profile_image_url"],
            verification_status="verified",
            location=maker_seed["location"],
            contact_email=maker_seed["email"],
        )
    )
    session.flush()


def get_or_create_customer_user(session, customer_role: Role) -> User:
    user = session.scalar(select(User).where(User.email == SEED_CUSTOMER["email"]))
    if user is not None:
        return user

    user = User(
        email=SEED_CUSTOMER["email"],
        full_name=SEED_CUSTOMER["full_name"],
        password_hash=hash_password("password123"),
        role=customer_role,
        is_active=True,
    )
    session.add(user)
    session.flush()
    return user


def seed_products() -> None:
    init_db()

    with SessionLocal() as session:
        ensure_system_roles(session)
        maker_role = get_or_create_maker_role(session)
        customer_role = session.scalar(select(Role).where(Role.name == "customer"))
        if customer_role is None:
            raise RuntimeError("Customer role is missing after role initialization.")
        customer_user = get_or_create_customer_user(session, customer_role)

        created_products = 0
        created_product_orders = 0
        created_commissions = 0

        for maker_seed in SEED_MAKERS:
            user = get_or_create_maker_user(session, maker_role, maker_seed)
            get_or_create_maker_profile(session, user, maker_seed)

            for product_seed in maker_seed["products"]:
                product = session.scalar(
                    select(Product).where(
                        Product.maker_id == user.id,
                        Product.title == product_seed["title"],
                    )
                )
                if product is None:
                    product = Product(
                        maker_id=user.id,
                        title=product_seed["title"],
                        description=product_seed["description"],
                        price=product_seed["price"],
                        stock_quantity=product_seed["stock_quantity"],
                        is_active=True,
                    )
                    session.add(product)
                    session.flush()
                    created_products += 1

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
                    for choice in choices:
                        if choice["label"] in existing_choice_labels:
                            continue
                        session.add(
                            ProductCustomizationChoice(
                                option_id=option.id,
                                label=choice["label"],
                                price_delta=choice["price_delta"],
                            )
                        )

                profile = session.scalar(select(MakerProfile).where(MakerProfile.user_id == user.id))
                if profile is not None:
                    profile.bio = maker_seed["bio"]
                    profile.specialization = maker_seed["specialization"]
                    profile.profile_image_url = maker_seed["profile_image_url"]
                    profile.verification_status = "verified"

        sample_orders = [
            {
                "product_title": "Speckled Tea Cup Set",
                "quantity": 1,
                "status": "in_progress",
                "updates": [
                    "Order confirmed. Clay has been prepared for the selected porcelain set.",
                    "Glaze samples for Forest Brushstroke pattern have been approved and firing is next.",
                ],
                "selections": {
                    "Material": "Porcelain",
                    "Pattern": "Forest Brushstroke",
                },
            },
            {
                "product_title": "Indigo Loom Scarf",
                "quantity": 2,
                "status": "pending",
                "updates": [
                    "Order received. Yarn has been reserved for the cotton-linen blend version.",
                ],
                "selections": {
                    "Material": "Cotton-Linen Blend",
                    "Length": "Long",
                },
            },
        ]

        for order_seed in sample_orders:
            product = session.scalar(select(Product).where(Product.title == order_seed["product_title"]))
            if product is None:
                continue

            existing_order = session.scalar(
                select(ProductOrder).where(
                    ProductOrder.customer_id == customer_user.id,
                    ProductOrder.product_id == product.id,
                )
            )
            if existing_order is None:
                option_map = {
                    option.name: option
                    for option in session.scalars(
                        select(ProductCustomizationOption).where(
                            ProductCustomizationOption.product_id == product.id
                        )
                    ).all()
                }

                order = ProductOrder(
                    product_id=product.id,
                    customer_id=customer_user.id,
                    maker_id=product.maker_id,
                    quantity=order_seed["quantity"],
                    total_price=product.price * order_seed["quantity"],
                    status=order_seed["status"],
                    customization_summary=", ".join(
                        f"{key}: {value}" for key, value in order_seed["selections"].items()
                    ),
                )
                session.add(order)
                session.flush()
                created_product_orders += 1

                total_delta = Decimal("0.00")
                for option_name, choice_label in order_seed["selections"].items():
                    option = option_map[option_name]
                    choice = session.scalar(
                        select(ProductCustomizationChoice).where(
                            ProductCustomizationChoice.option_id == option.id,
                            ProductCustomizationChoice.label == choice_label,
                        )
                    )
                    if choice is None:
                        continue
                    total_delta += Decimal(choice.price_delta)
                    session.add(
                        ProductOrderSelection(
                            order_id=order.id,
                            option_id=option.id,
                            choice_id=choice.id,
                        )
                    )

                order.total_price = (Decimal(product.price) + total_delta) * order_seed["quantity"]
                for message in order_seed["updates"]:
                    session.add(
                        ProductOrderProgressUpdate(
                            order_id=order.id,
                            message=message,
                        )
                    )

        session.commit()
        print(f"Seeded sample products. Created {created_products} new products.")
        print(f"Created {created_product_orders or created_commissions} new customer orders.")
        sample_commissions = [
            {
                "maker_email": "lila.ceramics@example.com",
                "title": "Custom ramen bowl set",
                "description": "A pair of deep bowls with a brushed matte exterior.",
                "customization_notes": "Prefer charcoal exterior, warm white interior, and slightly wider rim.",
                "budget": Decimal("78.00"),
                "status": "pending",
            },
            {
                "maker_email": "mara.wood@example.com",
                "title": "Personalized serving tray",
                "description": "Rectangular tray for coffee service.",
                "customization_notes": "Need walnut tone, rounded corners, and subtle carved initials at the back.",
                "budget": Decimal("64.00"),
                "status": "accepted",
            },
        ]

        makers_by_email = {
            maker.email: maker
            for maker in session.scalars(
                select(User)
                .join(Role, Role.id == User.role_id)
                .where(Role.name == "maker")
            ).all()
        }

        for commission_seed in sample_commissions:
            maker = makers_by_email[commission_seed["maker_email"]]
            existing_commission = session.scalar(
                select(Commission).where(
                    Commission.customer_id == customer_user.id,
                    Commission.maker_id == maker.id,
                    Commission.title == commission_seed["title"],
                )
            )
            if existing_commission is not None:
                continue

            session.add(
                Commission(
                    customer_id=customer_user.id,
                    maker_id=maker.id,
                    title=commission_seed["title"],
                    description=commission_seed["description"],
                    customization_notes=commission_seed["customization_notes"],
                    budget=commission_seed["budget"],
                    status=commission_seed["status"],
                )
            )
            created_commissions += 1

        session.commit()
        print(f"Created {created_commissions} new commission requests.")
        print("Sample maker login password: password123")
        print("Sample customer login: mina.customer@example.com / password123")


if __name__ == "__main__":
    seed_products()
