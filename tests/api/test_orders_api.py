import pytest

from tests.api import schemas

pytestmark = pytest.mark.api

ADDRESS = {"full_name": "Grace Hopper", "email": "grace@example.com", "address": "1 Navy Way", "zip_code": "10001"}


def test_empty_cart(auth_api, assert_schema):
    cart = assert_schema(auth_api.get("/cart").json(), schemas.CART)
    assert cart == {"items": [], "subtotal_cents": 0, "tax_cents": 0}


def test_add_to_cart_calculates_totals(auth_api, assert_schema):
    resp = auth_api.post("/cart", json={"product_id": 2, "quantity": 3})
    assert resp.status_code == 201
    cart = assert_schema(resp.json(), schemas.CART)
    assert cart["subtotal_cents"] == 3 * 2999
    assert cart["tax_cents"] == 720  # 8% of 89.97 = 7.1976 -> 7.20


@pytest.mark.parametrize("payload, status", [
    ({"product_id": 2, "quantity": 0}, 422),
    ({"product_id": 2, "quantity": -1}, 422),
    ({"product_id": 2, "quantity": 41}, 422),     # stock is 40
    ({"product_id": 10, "quantity": 1}, 422),     # out of stock
    ({"product_id": 999, "quantity": 1}, 404),
    ({"product_id": "2", "quantity": 1}, 400),
    ({"product_id": 2, "quantity": 1.5}, 400),
    ({"quantity": 1}, 400),
])
@pytest.mark.db
def test_add_to_cart_rejects_bad_input(auth_api, db, assert_schema, payload, status):
    resp = auth_api.post("/cart", json=payload)
    assert resp.status_code == status
    assert_schema(resp.json(), schemas.ERROR)
    assert db.cart_size("qa_lead") == 0


def test_remove_from_cart(auth_api):
    auth_api.post("/cart", json={"product_id": 5, "quantity": 1})
    assert auth_api.delete("/cart/5").status_code == 204
    assert auth_api.delete("/cart/5").status_code == 404
    assert auth_api.get("/cart").json()["items"] == []


@pytest.mark.smoke
@pytest.mark.db
def test_place_order_end_to_end(auth_api, db, assert_schema):
    auth_api.post("/cart", json={"product_id": 1, "quantity": 2})
    auth_api.post("/cart", json={"product_id": 11, "quantity": 5})
    resp = auth_api.post("/orders", json=ADDRESS)
    assert resp.status_code == 201
    order = assert_schema(resp.json(), schemas.ORDER)

    assert order["subtotal_cents"] == 2 * 8999 + 5 * 599
    assert order["total_cents"] == order["subtotal_cents"] + order["tax_cents"]
    row = db.query_one("SELECT * FROM orders WHERE id = ?", (order["id"],))
    assert row["total_cents"] == order["total_cents"]
    assert db.stock_of("KB-001") == 23
    assert db.stock_of("ST-011") == 195
    assert auth_api.get("/cart").json()["items"] == []

    listed = auth_api.get("/orders").json()
    assert listed["count"] == 1 and listed["items"][0]["id"] == order["id"]
    assert auth_api.get(f"/orders/{order['id']}").json() == order


@pytest.mark.parametrize("field, value", [
    ("email", "not-an-email"), ("zip_code", "123"), ("full_name", ""), ("address", "  "),
])
def test_order_validation_errors(auth_api, field, value):
    auth_api.post("/cart", json={"product_id": 1, "quantity": 1})
    resp = auth_api.post("/orders", json={**ADDRESS, field: value})
    assert resp.status_code == 422
    assert list(resp.json()["fields"]) == [field]


def test_order_with_empty_cart_conflicts(auth_api):
    assert auth_api.post("/orders", json=ADDRESS).status_code == 409


def test_users_cannot_see_each_others_orders(base_url, auth_api):
    from framework.api_client import ApiClient

    auth_api.post("/cart", json={"product_id": 1, "quantity": 1})
    order_id = auth_api.post("/orders", json=ADDRESS).json()["id"]

    other = ApiClient(base_url).login("standard_user", "secret_sauce")
    assert other.get(f"/orders/{order_id}").status_code == 404
    assert other.get("/orders").json()["count"] == 0
