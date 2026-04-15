from __future__ import annotations

from app.models import Commission, Product


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


def test_register_and_login_return_role(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "new.customer@example.com",
            "full_name": "New Customer",
            "password": "password123",
            "role": "customer",
        },
    )

    assert register_response.status_code == 201
    register_body = register_response.json()
    assert register_body["user"]["role"] == "customer"
    assert register_body["access_token"]

    login_response = client.post(
        "/auth/login",
        json={
            "email": "new.customer@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    assert login_response.json()["user"]["role"] == "customer"


def test_unauthenticated_and_wrong_role_requests_return_correct_codes(
    client,
    customer_user,
):
    unauthenticated_response = client.get("/wishlist")
    assert unauthenticated_response.status_code == 401

    customer_headers = auth_headers_for(client, customer_user.email)
    forbidden_response = client.get("/maker/products", headers=customer_headers)
    assert forbidden_response.status_code == 403


def test_customer_only_sees_own_commissions(
    client,
    db_session,
    customer_user,
    second_customer_user,
    maker_user,
):
    own_commission = Commission(
        customer_id=customer_user.id,
        maker_id=maker_user.id,
        title="Own commission",
        description="Visible to owner",
        customization_notes="Blue finish",
        budget=25,
        status="pending",
    )
    other_commission = Commission(
        customer_id=second_customer_user.id,
        maker_id=maker_user.id,
        title="Other commission",
        description="Should not be visible",
        customization_notes="Hidden",
        budget=30,
        status="pending",
    )
    db_session.add_all([own_commission, other_commission])
    db_session.commit()

    response = client.get(
        "/commissions",
        headers=auth_headers_for(client, customer_user.email),
    )

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert "Own commission" in titles
    assert "Other commission" not in titles


def test_maker_can_only_post_wip_updates_for_assigned_commission(
    client,
    db_session,
    customer_user,
    maker_user,
    second_maker_user,
):
    own_commission = Commission(
        customer_id=customer_user.id,
        maker_id=maker_user.id,
        title="Assigned to maker one",
        description="Allowed update",
        customization_notes="Oak wood",
        budget=50,
        status="accepted",
    )
    other_commission = Commission(
        customer_id=customer_user.id,
        maker_id=second_maker_user.id,
        title="Assigned to maker two",
        description="Forbidden update",
        customization_notes="Walnut",
        budget=80,
        status="accepted",
    )
    db_session.add_all([own_commission, other_commission])
    db_session.commit()
    db_session.refresh(own_commission)
    db_session.refresh(other_commission)

    maker_headers = auth_headers_for(client, maker_user.email)

    success_response = client.post(
        f"/commissions/{own_commission.id}/updates",
        headers=maker_headers,
        json={"message": "Started carving the base.", "image_url": None},
    )
    assert success_response.status_code == 201
    assert success_response.json()["message"] == "Started carving the base."

    forbidden_response = client.post(
        f"/commissions/{other_commission.id}/updates",
        headers=maker_headers,
        json={"message": "This should fail.", "image_url": None},
    )
    assert forbidden_response.status_code == 404


def test_customer_wishlist_is_idempotent(client, db_session, customer_user, maker_user):
    product = Product(
        maker_id=maker_user.id,
        title="Clay Mug",
        description="Simple mug",
        price=18,
        stock_quantity=4,
        is_active=True,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    headers = auth_headers_for(client, customer_user.email)
    first_response = client.post("/wishlist", headers=headers, json={"product_id": product.id})
    second_response = client.post("/wishlist", headers=headers, json={"product_id": product.id})
    list_response = client.get("/wishlist", headers=headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert len(list_response.json()) == 1


def test_admin_can_manage_users_but_non_admin_cannot(
    client,
    admin_user,
    customer_user,
):
    customer_headers = auth_headers_for(client, customer_user.email)
    forbidden_response = client.put(
        f"/admin/users/{customer_user.id}",
        headers=customer_headers,
        json={"is_active": False},
    )
    assert forbidden_response.status_code == 403

    admin_headers = auth_headers_for(client, admin_user.email)
    success_response = client.put(
        f"/admin/users/{customer_user.id}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert success_response.status_code == 200
    assert success_response.json()["is_active"] is False
