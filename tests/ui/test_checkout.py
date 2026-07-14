import pytest

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.checkout_page import CheckoutPage, ConfirmationPage

pytestmark = pytest.mark.ui

VALID_ADDRESS = {
    "full_name": "Ada Lovelace",
    "email": "ada@example.com",
    "address": "12 Analytical Engine Way",
    "zip_code": "80202",
}


@pytest.fixture
def cart_with_items(logged_in, base_url):
    catalog = CatalogPage(logged_in, base_url)
    for name in ("Mechanical Keyboard", "Clean Code"):
        catalog.open().add_to_cart(name)
    return CartPage(logged_in, base_url)


@pytest.mark.smoke
@pytest.mark.db
def test_end_to_end_purchase_is_saved_correctly(cart_with_items, db):
    """Full happy path, then check the database agrees with what the UI showed."""
    stock_before = {sku: db.stock_of(sku) for sku in ("KB-001", "BK-005")}

    checkout = cart_with_items.proceed_to_checkout()
    ui_totals = checkout.totals()
    assert ui_totals == {"subtotal": 12498, "tax": 1000, "total": 13498}

    checkout.fill(**VALID_ADDRESS).place_order()
    confirmation = ConfirmationPage(checkout.driver, checkout.base_url)
    assert confirmation.text_of(confirmation.HEADING) == "Thank you for your order!"
    assert confirmation.skus() == ["BK-005", "KB-001"]
    assert confirmation.total_cents == ui_totals["total"]

    # -- SQL validation -------------------------------------------------
    order = db.latest_order("standard_user")
    assert order["id"] == confirmation.order_number
    assert (order["subtotal_cents"], order["tax_cents"], order["total_cents"]) == (12498, 1000, 13498)
    assert order["email"] == VALID_ADDRESS["email"]
    assert order["status"] == "PLACED"
    assert db.order_items(order["id"]) == [
        {"sku": "BK-005", "quantity": 1, "unit_price_cents": 3499},
        {"sku": "KB-001", "quantity": 1, "unit_price_cents": 8999},
    ]
    assert db.stock_of("KB-001") == stock_before["KB-001"] - 1
    assert db.stock_of("BK-005") == stock_before["BK-005"] - 1
    assert db.cart_size("standard_user") == 0
    assert confirmation.cart_count == 0


@pytest.mark.regression
@pytest.mark.parametrize("field, value, message", [
    ("full_name", "   ", "Full name is required."),
    ("email", "ada.example.com", "Enter a valid email address."),
    ("email", "ada@example", "Enter a valid email address."),
    ("address", "", "Address is required."),
    ("zip_code", "8020", "ZIP code must be 5 digits."),
    ("zip_code", "80202-1234", "ZIP code must be 5 digits."),
    ("zip_code", "ABCDE", "ZIP code must be 5 digits."),
])
@pytest.mark.db
def test_checkout_field_validation(cart_with_items, db, field, value, message):
    checkout = cart_with_items.proceed_to_checkout()
    checkout.fill(**{**VALID_ADDRESS, field: value}).place_order()
    assert checkout.errors() == {field: message}
    assert checkout.current_path == "/checkout"
    assert db.latest_order("standard_user") is None, "invalid checkout must not create an order"


@pytest.mark.regression
def test_checkout_keeps_entered_values_after_error(cart_with_items):
    checkout = cart_with_items.proceed_to_checkout()
    checkout.fill(**{**VALID_ADDRESS, "zip_code": "1"}).place_order()
    assert checkout.find(("id", "email")).get_attribute("value") == VALID_ADDRESS["email"]


@pytest.mark.regression
def test_empty_cart_cannot_checkout(logged_in, base_url):
    page = CheckoutPage(logged_in, base_url).open()
    assert page.current_path == "/cart"
    assert page.flash_message == "Your cart is empty."


@pytest.mark.regression
def test_order_shows_in_history(cart_with_items):
    checkout = cart_with_items.proceed_to_checkout()
    checkout.fill(**VALID_ADDRESS).place_order()
    number = ConfirmationPage(checkout.driver, checkout.base_url).order_number
    history = checkout.open("/orders")
    rows = history.find_all(("css selector", "#orders-table .order-row"))
    assert len(rows) == 1 and f"#{number}" in rows[0].text
