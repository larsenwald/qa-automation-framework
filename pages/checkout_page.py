from selenium.webdriver.common.by import By

from .base_page import BasePage
from .catalog_page import parse_money


class CheckoutPage(BasePage):
    path = "/checkout"

    FIELDS = ("full_name", "email", "address", "zip_code")
    PLACE_ORDER = (By.ID, "place-order")
    SUBTOTAL = (By.ID, "summary-subtotal")
    TAX = (By.ID, "summary-tax")
    TOTAL = (By.ID, "summary-total")
    FIELD_ERRORS = (By.CSS_SELECTOR, ".field-error")

    @staticmethod
    def error_for(field):
        return (By.ID, f"{field}-error")

    def fill(self, **values):
        for field in self.FIELDS:
            if field in values:
                self.type((By.ID, field), values[field])
        return self

    def place_order(self):
        self.click_and_wait_for_reload(self.PLACE_ORDER)
        return self

    def totals(self):
        return {
            "subtotal": parse_money(self.text_of(self.SUBTOTAL)),
            "tax": parse_money(self.text_of(self.TAX)),
            "total": parse_money(self.text_of(self.TOTAL)),
        }

    def errors(self):
        return {
            el.get_attribute("id").removesuffix("-error"): el.text
            for el in self.find_all(self.FIELD_ERRORS)
        }


class ConfirmationPage(BasePage):
    HEADING = (By.ID, "confirmation-heading")
    ORDER_NUMBER = (By.ID, "order-number")
    STATUS = (By.ID, "order-status")
    TOTAL = (By.ID, "order-total")
    ITEMS = (By.CSS_SELECTOR, "#order-items .order-item")

    @property
    def order_number(self):
        return int(self.text_of(self.ORDER_NUMBER))

    @property
    def total_cents(self):
        return parse_money(self.text_of(self.TOTAL))

    def skus(self):
        return sorted(el.get_attribute("data-sku") for el in self.find_all(self.ITEMS))
