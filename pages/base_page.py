"""Shared plumbing for every page object.

Rule of the framework: tests never call driver.find_element or time.sleep directly.
They go through page objects, and page objects go through these explicit-wait helpers.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

Locator = tuple[str, str]

DEFAULT_TIMEOUT = 10


class BasePage:
    path = "/"

    # Header, present on every page
    CART_COUNT = (By.ID, "cart-count")
    CURRENT_USER = (By.ID, "current-user")
    LOGOUT_LINK = (By.ID, "logout-link")
    FLASH = (By.CSS_SELECTOR, ".flash")

    def __init__(self, driver, base_url, timeout=DEFAULT_TIMEOUT):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -- navigation -------------------------------------------------------
    def open(self, path=None):
        self.driver.get(self.base_url + (path or self.path))
        return self

    @property
    def current_path(self):
        return self.driver.current_url.removeprefix(self.base_url)

    # -- waits -------------------------------------------------------------
    def wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout)

    def find(self, locator: Locator) -> WebElement:
        return self.wait().until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        # Returns [] instead of timing out: "no results" is a valid state to assert on.
        return self.driver.find_elements(*locator)

    def click(self, locator: Locator):
        self.wait().until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator: Locator, text, clear=True):
        el = self.find(locator)
        if clear:
            el.clear()
        el.send_keys(text)

    def text_of(self, locator: Locator) -> str:
        return self.find(locator).text.strip()

    def select_by_value(self, locator: Locator, value):
        Select(self.find(locator)).select_by_value(value)

    def is_visible(self, locator: Locator, timeout=2) -> bool:
        try:
            self.wait(timeout).until(EC.visibility_of_element_located(locator))
            return True
        except Exception:
            return False

    def wait_for_text(self, locator: Locator, text, timeout=None):
        self.wait(timeout).until(EC.text_to_be_present_in_element(locator, text))

    def wait_for_url_contains(self, fragment, timeout=None):
        self.wait(timeout).until(EC.url_contains(fragment))

    # -- header helpers ------------------------------------------------------
    @property
    def cart_count(self) -> int:
        return int(self.text_of(self.CART_COUNT))

    @property
    def flash_message(self) -> str:
        return self.text_of(self.FLASH)

    @property
    def logged_in_user(self):
        return self.text_of(self.CURRENT_USER) if self.is_visible(self.CURRENT_USER, 1) else None
