from __future__ import annotations

from app.models import Commission, MakerProfile, Product, Review, ShopVerification


def auth_headers_for(client, email: str, password: str = "password123") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_product(db_session, maker_id: int, title: str = "Handmade Bowl") -> Product:
    product = Product(
        maker_id=maker_id,
        title=title,
        description="Stoneware bowl",
        price=35,
        stock_quantity=8,
        is_active=True,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_maker_can_manage_only_own_products(client, maker_user, second_maker_user):
    maker_headers = auth_headers_for(client, maker_user.email)
    second_maker_headers = auth_headers_for(client, second_maker_user.email)

    create_response = client.post(
        "/products",
        headers=maker_headers,
        json={
            "title": "Woven Basket",
            "description": "Natural fiber basket",
            "price": 28,
            "stock_quantity": 6,
            "is_active": True,
        },
    )
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    own_list_response = client.get("/maker/products", headers=maker_headers)
    assert own_list_response.status_code == 200
    assert len(own_list_response.json()) == 1
    assert own_list_response.json()[0]["title"] == "Woven Basket"

    forbidden_update = client.put(
        f"/products/{product_id}",
        headers=second_maker_headers,
        json={
          "title": "Changed",
          "description": "Should not update",
          "price": 40,
          "stock_quantity": 2,
          "is_active": True,
        },
    )
    assert forbidden_update.status_code == 404

    forbidden_delete = client.delete(f"/products/{product_id}", headers=second_maker_headers)
    assert forbidden_delete.status_code == 404


def test_product_reviews_require_customer_and_prevent_duplicates(
    client,
    db_session,
    customer_user,
    maker_user,
):
    product = create_product(db_session, maker_user.id)

    customer_headers = auth_headers_for(client, customer_user.email)
    create_review_response = client.post(
        f"/products/{product.id}/reviews",
        headers=customer_headers,
        json={"rating": 5, "comment": "Excellent finish."},
    )
    assert create_review_response.status_code == 201
    assert create_review_response.json()["rating"] == 5

    duplicate_review_response = client.post(
        f"/products/{product.id}/reviews",
        headers=customer_headers,
        json={"rating": 4, "comment": "Second review"},
    )
    assert duplicate_review_response.status_code == 409

    maker_headers = auth_headers_for(client, maker_user.email)
    wrong_role_response = client.post(
        f"/products/{product.id}/reviews",
        headers=maker_headers,
        json={"rating": 4, "comment": "Maker cannot review here"},
    )
    assert wrong_role_response.status_code == 403


def test_commission_review_requires_completed_owned_commission(
    client,
    db_session,
    customer_user,
    second_customer_user,
    maker_user,
):
    pending_commission = Commission(
        customer_id=customer_user.id,
        maker_id=maker_user.id,
        title="Pending commission",
        description="Still in progress",
        customization_notes="Matte black",
        budget=45,
        status="pending",
    )
    other_customer_commission = Commission(
        customer_id=second_customer_user.id,
        maker_id=maker_user.id,
        title="Other customer commission",
        description="Not owned",
        customization_notes="Gold trim",
        budget=60,
        status="completed",
    )
    completed_commission = Commission(
        customer_id=customer_user.id,
        maker_id=maker_user.id,
        title="Completed commission",
        description="Ready for review",
        customization_notes="Blue glaze",
        budget=70,
        status="completed",
    )
    db_session.add_all([pending_commission, other_customer_commission, completed_commission])
    db_session.commit()
    db_session.refresh(pending_commission)
    db_session.refresh(other_customer_commission)
    db_session.refresh(completed_commission)

    customer_headers = auth_headers_for(client, customer_user.email)

    pending_response = client.post(
        f"/commissions/{pending_commission.id}/reviews",
        headers=customer_headers,
        json={"rating": 4, "comment": "Too early"},
    )
    assert pending_response.status_code == 422

    not_owned_response = client.post(
        f"/commissions/{other_customer_commission.id}/reviews",
        headers=customer_headers,
        json={"rating": 5, "comment": "Should not see this"},
    )
    assert not_owned_response.status_code == 404

    success_response = client.post(
        f"/commissions/{completed_commission.id}/reviews",
        headers=customer_headers,
        json={"rating": 5, "comment": "Great custom work."},
    )
    assert success_response.status_code == 201


def test_admin_product_moderation_hides_product_from_catalog(
    client,
    db_session,
    admin_user,
    maker_user,
):
    product = create_product(db_session, maker_user.id, title="Moderated Lamp")

    public_before = client.get("/products")
    assert public_before.status_code == 200
    assert any(item["id"] == product.id for item in public_before.json())

    admin_headers = auth_headers_for(client, admin_user.email)
    delete_response = client.delete(f"/admin/products/{product.id}", headers=admin_headers)
    assert delete_response.status_code == 204

    public_after = client.get("/products")
    assert public_after.status_code == 200
    assert all(item["id"] != product.id for item in public_after.json())


def test_admin_review_moderation_removes_review_from_admin_list_and_public_product(
    client,
    db_session,
    admin_user,
    customer_user,
    maker_user,
):
    product = create_product(db_session, maker_user.id, title="Reviewed Plate")
    review = Review(
        customer_id=customer_user.id,
        product_id=product.id,
        commission_id=None,
        rating=2,
        comment="Inappropriate review",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)

    admin_headers = auth_headers_for(client, admin_user.email)
    admin_list_before = client.get("/admin/reviews", headers=admin_headers)
    assert admin_list_before.status_code == 200
    assert any(item["id"] == review.id for item in admin_list_before.json())

    delete_response = client.delete(f"/admin/reviews/{review.id}", headers=admin_headers)
    assert delete_response.status_code == 204

    admin_list_after = client.get("/admin/reviews", headers=admin_headers)
    assert all(item["id"] != review.id for item in admin_list_after.json())

    product_detail = client.get(f"/products/{product.id}")
    assert product_detail.status_code == 200
    assert product_detail.json()["reviews"] == []


def test_admin_verification_updates_maker_profile_and_record(
    client,
    db_session,
    admin_user,
    maker_user,
):
    profile = MakerProfile(
        user_id=maker_user.id,
        shop_name="Maker Studio",
        bio="Ceramics",
        specialization="Pottery",
        profile_image_url=None,
        verification_status="unverified",
        contact_email=maker_user.email,
    )
    verification = ShopVerification(
        maker_id=maker_user.id,
        document_url="https://example.com/document.pdf",
        status="pending",
        notes=None,
    )
    db_session.add_all([profile, verification])
    db_session.commit()

    admin_headers = auth_headers_for(client, admin_user.email)
    response = client.put(
        f"/admin/verifications/{maker_user.id}",
        headers=admin_headers,
        json={"status": "verified", "notes": "Shop documents approved."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "verified"
    assert body["profile_verification_status"] == "verified"
    assert body["notes"] == "Shop documents approved."
