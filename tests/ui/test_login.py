import pytest

from pages.base_page import BasePage
from pages.login_page import LoginPage
from tests.data import cases

pytestmark = pytest.mark.ui


@pytest.mark.smoke
@pytest.mark.parametrize("case", cases("login_cases.json", "valid"))
def test_valid_login(driver, base_url, case):
    page = LoginPage(driver, base_url).open().login(case["username"], case["password"])
    page.wait_for_text(page.CURRENT_USER, case["username"])
    assert page.current_path == "/"
    assert f"Welcome back, {case['username']}!" in page.flash_message


@pytest.mark.regression
@pytest.mark.parametrize("case", cases("login_cases.json", "invalid"))
def test_invalid_login_is_rejected(driver, base_url, case):
    page = LoginPage(driver, base_url).open().login(case["username"], case["password"])
    assert page.error_message == "Invalid username or password."
    assert page.logged_in_user is None


@pytest.mark.regression
def test_password_field_is_masked(driver, base_url):
    page = LoginPage(driver, base_url).open()
    assert page.find(page.PASSWORD).get_attribute("type") == "password"


@pytest.mark.regression
def test_logout_ends_session(driver, base_url):
    page = LoginPage(driver, base_url).login_as("standard_user", "secret_sauce")
    page.click(page.LOGOUT_LINK)
    assert page.current_path == "/login"
    # The cart is protected, so going back to it should bounce to login.
    BasePage(driver, base_url).open("/cart")
    assert page.current_path.startswith("/login")


@pytest.mark.regression
def test_protected_page_returns_user_after_login(driver, base_url):
    BasePage(driver, base_url).open("/orders")
    page = LoginPage(driver, base_url)
    assert page.current_path.startswith("/login")
    page.login("standard_user", "secret_sauce")
    page.wait_for_url_contains("/orders")
    assert page.current_path == "/orders"


@pytest.mark.regression
@pytest.mark.parametrize("evil", ["https://evil.example", "//evil.example", "/\evil.example"])
def test_login_ignores_external_next_url(driver, base_url, evil):
    page = LoginPage(driver, base_url).open(f"/login?next={evil}")
    page.login("standard_user", "secret_sauce")
    page.wait_for_text(page.CURRENT_USER, "standard_user")
    assert driver.current_url.startswith(base_url)
    assert page.current_path == "/"
