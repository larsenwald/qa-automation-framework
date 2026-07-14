from dataclasses import dataclass

from selenium.webdriver.common.by import By

from .base_page import BasePage
from .catalog_page import parse_money


@dataclass
class CartLine:
    sku: str
    name: str
    quantity: int
    total_cents: int


class CartPage(BasePage):
    path = "/cart"

    ROWS = (By.CSS_SELECTOR, "#cart-table tr.cart-row")
    SUBTOTAL = (By.ID, "cart-subtotal")
    EMPTY = (By.ID, "empty-cart")
    CHECKOUT = (By.ID, "checkout-button")

    @staticmethod
    def remove_button(sku):
        return (By.CSS_SELECTOR, f"tr.cart-row[data-sku='{sku}'] button.remove-item")

    def lines(self) -> list[CartLine]:
        return [
            CartLine(
                sku=row.get_attribute("data-sku"),
                name=row.find_element(By.CSS_SELECTOR, ".item-name").text,
                quantity=int(row.find_element(By.CSS_SELECTOR, ".item-qty").text),
                total_cents=parse_money(row.find_element(By.CSS_SELECTOR, ".item-total").text),
            )
            for row in self.find_all(self.ROWS)
        ]

    def line(self, sku) -> CartLine:
        return next(line for line in self.lines() if line.sku == sku)

    @property
    def subtotal_cents(self):
        return parse_money(self.text_of(self.SUBTOTAL))

    def is_empty(self):
        return self.is_visible(self.EMPTY)

    def remove(self, sku):
        self.click_and_wait_for_reload(self.remove_button(sku))
        return self

    def proceed_to_checkout(self):
        self.click_and_wait_for_reload(self.CHECKOUT)
        from .checkout_page import CheckoutPage
        return CheckoutPage(self.driver, self.base_url)
