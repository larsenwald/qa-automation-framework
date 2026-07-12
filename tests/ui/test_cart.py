import pytest

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage

pytestmark = pytest.mark.ui


@pytest.fixture
def catalog(logged_in, base_url):
    return CatalogPage(logged_in, base_url).open()


@pytest.mark.smoke
def test_add_to_cart_updates_badge_and_cart(catalog, base_url):
    assert catalog.cart_count == 0
    catalog.open().add_to_cart("Wireless Mouse")
    cart = CartPage(catalog.driver, base_url)
    assert cart.cart_count == 1
    assert cart.line("MS-002").quantity == 1
    assert cart.subtotal_cents == 2999


@pytest.mark.regression
def test_adding_same_item_twice_increments_quantity(catalog, base_url):
    catalog.add_to_cart("Sticker Pack")
    catalog.open().add_to_cart("Sticker Pack")
    cart = CartPage(catalog.driver, base_url)
    assert [(line.sku, line.quantity) for line in cart.lines()] == [("ST-011", 2)]
    assert cart.line("ST-011").total_cents == 2 * 599


@pytest.mark.regression
def test_subtotal_is_sum_of_line_totals(catalog, base_url):
    for name in ("Mechanical Keyboard", "Clean Code", "Bug Hunter Mug"):
        catalog.open().add_to_cart(name)
    cart = CartPage(catalog.driver, base_url)
    assert cart.subtotal_cents == sum(line.total_cents for line in cart.lines()) == 8999 + 3499 + 1499


@pytest.mark.regression
def test_remove_item_empties_cart(catalog, base_url):
    catalog.add_to_cart("Desk Lamp")
    cart = CartPage(catalog.driver, base_url).remove("DL-009")
    assert cart.is_empty()
    assert cart.cart_count == 0


@pytest.mark.regression
def test_add_multiple_from_product_page(logged_in, base_url):
    page = ProductPage(logged_in, base_url).open_id(2)
    assert page.title == "Wireless Mouse"
    page.add_quantity(3)
    cart = CartPage(logged_in, base_url)
    assert cart.line("MS-002").quantity == 3
    assert cart.subtotal_cents == 3 * 2999


@pytest.mark.regression
def test_anonymous_add_to_cart_goes_to_login_then_catalog(driver, base_url):
    catalog = CatalogPage(driver, base_url).open()
    # Header shows no cart for guests, so click the button directly.
    catalog.click_and_wait_for_reload(catalog.add_button_for("Wireless Mouse"))
    login = LoginPage(driver, base_url)
    assert login.current_path.startswith("/login")
    login.login("standard_user", "secret_sauce")
    login.wait_for_text(login.CURRENT_USER, "standard_user")
    assert "Method Not Allowed" not in driver.page_source
    assert login.current_path == "/"
