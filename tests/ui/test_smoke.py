import pytest
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


@pytest.mark.smoke
def test_home_page_loads(driver, base_url):
    page = BasePage(driver, base_url).open()
    assert "ShopLite" in driver.title
    assert page.is_visible((By.ID, "product-grid"))
