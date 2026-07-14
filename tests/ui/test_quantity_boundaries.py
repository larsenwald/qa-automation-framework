"""Boundary-value tests for cart quantity.

The quantity box has min="1" in HTML, but client-side validation is a convenience, not a control.
These tests strip it and confirm the *server* rejects bad values too.
"""
import pytest

from pages.cart_page import CartPage
from pages.product_page import ProductPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]

KEYBOARD_ID, KEYBOARD_SKU, KEYBOARD_STOCK = 1, "KB-001", 25


@pytest.fixture
def product(logged_in, base_url):
    return ProductPage(logged_in, base_url).open_id(KEYBOARD_ID).bypass_client_validation()


@pytest.mark.parametrize("qty", [1, 2, KEYBOARD_STOCK - 1, KEYBOARD_STOCK])
def test_valid_quantities_are_accepted(product, db, qty):
    product.add_quantity(qty)
    assert CartPage(product.driver, product.base_url).line(KEYBOARD_SKU).quantity == qty
    assert db.cart_size("standard_user") == qty


@pytest.mark.db
@pytest.mark.parametrize("qty", [0, -1, -50, KEYBOARD_STOCK + 1, 9999])
def test_invalid_quantities_are_rejected(product, db, qty):
    product.add_quantity(qty)
    assert "Quantity must be between 1 and" in product.flash_message
    assert db.cart_size("standard_user") == 0


@pytest.mark.db
def test_cart_total_cannot_exceed_stock_across_adds(product, db):
    product.add_quantity(20)
    ProductPage(product.driver, product.base_url).open_id(KEYBOARD_ID).add_quantity(10)
    assert db.cart_size("standard_user") == 20, "second add would exceed the 25 in stock"
