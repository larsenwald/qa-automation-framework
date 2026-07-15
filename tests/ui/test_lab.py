"""Alerts, iframes, multiple windows and dynamic content."""
import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from pages.lab_pages import AlertsPage, DynamicPage, FramesPage, WindowsPage

pytestmark = [pytest.mark.ui, pytest.mark.regression]


# -- JavaScript alerts ------------------------------------------------------------

def test_simple_alert_text_and_accept(driver, base_url):
    page = AlertsPage(driver, base_url).open()
    alert = page.trigger(page.ALERT_BTN)
    assert alert.text == "Your session will expire in 5 minutes."
    alert.accept()
    assert page.result == "Alert acknowledged"


@pytest.mark.parametrize("accept, expected", [(True, "Cart cleared"), (False, "Kept items")])
def test_confirm_dialog(driver, base_url, accept, expected):
    page = AlertsPage(driver, base_url).open()
    alert = page.trigger(page.CONFIRM_BTN)
    assert alert.text == "Remove all items from your cart?"
    alert.accept() if accept else alert.dismiss()
    assert page.result == expected


@pytest.mark.parametrize("code, expected", [
    ("SAVE10", "Coupon SAVE10 applied: 10% off"),
    ("  save10 ", "Coupon SAVE10 applied: 10% off"),
    ("FREE100", "Invalid coupon: FREE100"),
])
def test_prompt_dialog(driver, base_url, code, expected):
    page = AlertsPage(driver, base_url).open()
    alert = page.trigger(page.PROMPT_BTN)
    alert.send_keys(code)
    alert.accept()
    assert page.result == expected


def test_prompt_cancel(driver, base_url):
    page = AlertsPage(driver, base_url).open()
    page.trigger(page.PROMPT_BTN).dismiss()
    assert page.result == "Coupon cancelled"


# -- iframes ------------------------------------------------------------------------

def test_chat_widget_inside_iframe(driver, base_url):
    page = FramesPage(driver, base_url).open()
    with page.inside_chat():
        assert page.send_message("Where is my refund?") == "Refunds are processed within 5 business days."
        assert page.send_message("hello") == "Thanks! An agent will reply shortly."
    # Back in the main document, the page heading is reachable again.
    assert page.text_of(page.HEADING) == "Need help?"


def test_iframe_elements_not_visible_from_main_document(driver, base_url):
    page = FramesPage(driver, base_url).open()
    with pytest.raises(NoSuchElementException):
        driver.find_element(*page.CHAT_INPUT)


# -- windows & tabs -------------------------------------------------------------------

@pytest.mark.parametrize("trigger", ["NEW_TAB_LINK", "POPUP_BUTTON"])
def test_policy_opens_in_new_window(driver, base_url, trigger):
    page = WindowsPage(driver, base_url).open()
    original = page.open_and_switch(getattr(page, trigger))
    assert page.text_of(page.POLICY_HEADING) == "Return policy"
    assert page.text_of(page.RETURN_DAYS) == "30"

    driver.close()
    driver.switch_to.window(original)
    assert len(driver.window_handles) == 1
    assert page.current_path == "/lab/windows"


# -- dynamic content ------------------------------------------------------------------

def test_recommendations_load_after_random_delay(driver, base_url):
    page = DynamicPage(driver, base_url).open()
    assert page.find_all(page.REC_ITEMS) == []
    assert page.load_recommendations() == ["Wireless Mouse", "Desk Lamp", "Sticker Pack"]


def test_flash_sale_button_enables_after_countdown(driver, base_url):
    page = DynamicPage(driver, base_url).open()
    assert not page.find(page.CLAIM_BTN).is_enabled()
    page.wait(6).until(EC.element_to_be_clickable(page.CLAIM_BTN))
    page.click(page.CLAIM_BTN)
    assert page.text_of(page.DEAL_STATUS) == "Deal claimed!"
