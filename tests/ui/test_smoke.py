import pytest


@pytest.mark.smoke
def test_home_page_loads(driver, base_url):
    driver.get(base_url)
    assert "ShopLite" in driver.title
    assert driver.find_element("id", "product-grid").is_displayed()
