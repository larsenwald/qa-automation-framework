import pytest

from tests.api import schemas

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_health(api):
    resp = api.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    assert resp.headers["Content-Type"].startswith("application/json")


@pytest.mark.smoke
def test_list_products_matches_schema(api, assert_schema):
    resp = api.get("/products")
    assert resp.status_code == 200
    body = assert_schema(resp.json(), schemas.PRODUCT_LIST)
    assert body["count"] == len(body["items"]) == 12


@pytest.mark.db
def test_product_list_matches_database(api, db):
    """The API and the database must agree on every product's price and stock."""
    api_rows = {p["sku"]: (p["price_cents"], p["stock"]) for p in api.get("/products").json()["items"]}
    db_rows = {r["sku"]: (r["price_cents"], r["stock"]) for r in db.query("SELECT sku, price_cents, stock FROM products")}
    assert api_rows == db_rows


@pytest.mark.parametrize("params, expected_count", [
    ({"category": "Books"}, 3),
    ({"category": "Nope"}, 0),
    ({"q": "desk"}, 2),
    ({"q": "desk", "category": "Home"}, 2),
    ({"q": "desk", "category": "Books"}, 0),
])
def test_filter_products(api, params, expected_count):
    body = api.get("/products", params=params).json()
    assert body["count"] == expected_count
    if "category" in params:
        assert all(p["category"] == params["category"] for p in body["items"])


def test_get_single_product(api, assert_schema):
    product = assert_schema(api.get("/products/1").json(), schemas.PRODUCT)
    assert product["sku"] == "KB-001"
    assert product["in_stock"] is True


def test_out_of_stock_flag(api):
    plant = api.get("/products/10").json()
    assert plant["stock"] == 0 and plant["in_stock"] is False


@pytest.mark.parametrize("product_id", [0, 999, 2**31])
def test_unknown_product_returns_404_json(api, assert_schema, product_id):
    resp = api.get(f"/products/{product_id}")
    assert resp.status_code == 404
    assert_schema(resp.json(), schemas.ERROR)


def test_sql_injection_in_search_is_harmless(api, db):
    resp = api.get("/products", params={"q": "'; DROP TABLE products; --"})
    assert resp.status_code == 200
    assert resp.json()["count"] == 0
    assert db.scalar("SELECT COUNT(*) FROM products") == 12
