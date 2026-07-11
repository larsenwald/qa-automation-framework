from selenium.webdriver.common.by import By

from .base_page import BasePage
from .catalog_page import parse_money


class ProductPage(BasePage):
    TITLE = (By.ID, "product-title")
    PRICE = (By.ID, "product-price")
    STOCK = (By.ID, "product-stock")
    QUANTITY = (By.ID, "quantity")
    ADD = (By.ID, "add-to-cart")

    def open_id(self, product_id):
        return self.open(f"/product/{product_id}")

    @property
    def title(self):
        return self.text_of(self.TITLE)

    @property
    def price_cents(self):
        return parse_money(self.text_of(self.PRICE))

    @property
    def stock(self):
        return int(self.text_of(self.STOCK).split()[0])

    def add_quantity(self, qty):
        self.type(self.QUANTITY, str(qty))
        self.click_and_wait_for_reload(self.ADD)
        return self

    def bypass_client_validation(self):
        """Strip the HTML5 min/max attributes so we can check the *server* validates too."""
        self.driver.execute_script(
            "const q = document.getElementById('quantity'); q.removeAttribute('min'); q.removeAttribute('max');"
        )
        return self
