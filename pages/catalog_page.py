from dataclasses import dataclass

from selenium.webdriver.common.by import By

from .base_page import BasePage


def parse_money(text):
    return round(float(text.replace("$", "").replace(",", "")) * 100)


@dataclass
class ProductCard:
    sku: str
    name: str
    price_cents: int
    in_stock: bool


class CatalogPage(BasePage):
    path = "/"

    SEARCH = (By.ID, "search")
    CATEGORY = (By.ID, "category")
    SORT = (By.ID, "sort")
    APPLY = (By.ID, "search-button")
    RESULT_COUNT = (By.ID, "result-count")
    NO_RESULTS = (By.ID, "no-results")
    CARDS = (By.CSS_SELECTOR, "#product-grid .product-card")

    @staticmethod
    def card_by_sku(sku):
        return (By.CSS_SELECTOR, f".product-card[data-sku='{sku}']")

    @staticmethod
    def add_button_for(name):
        # XPath walks from the product name up to its card, then down to the button.
        return (By.XPATH, f"//a[contains(@class,'product-name') and normalize-space()='{name}']"
                          f"/ancestor::div[contains(@class,'product-card')]//button[contains(@class,'add-to-cart')]")

    def search(self, text="", category="", sort=None):
        self.type(self.SEARCH, text)
        self.select_by_value(self.CATEGORY, category)
        if sort:
            self.select_by_value(self.SORT, sort)
        self.click_and_wait_for_reload(self.APPLY)
        return self

    def products(self) -> list[ProductCard]:
        result = []
        for card in self.find_all(self.CARDS):
            result.append(ProductCard(
                sku=card.get_attribute("data-sku"),
                name=card.find_element(By.CSS_SELECTOR, ".product-name").text.strip(),
                price_cents=parse_money(card.find_element(By.CSS_SELECTOR, ".product-price").text),
                in_stock=not card.find_elements(By.CSS_SELECTOR, ".out-of-stock"),
            ))
        return result

    def add_to_cart(self, product_name):
        count_before = self.cart_count
        self.click_and_wait_for_reload(self.add_button_for(product_name))
        assert self.cart_count > count_before, f"cart count did not increase after adding {product_name}"
        return self

    def open_product(self, product_name):
        self.click((By.LINK_TEXT, product_name))
        from .product_page import ProductPage
        return ProductPage(self.driver, self.base_url)
