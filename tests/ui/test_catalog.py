import pytest

from pages.catalog_page import CatalogPage

pytestmark = pytest.mark.ui


@pytest.fixture
def catalog(driver, base_url):
    return CatalogPage(driver, base_url).open()


@pytest.mark.smoke
def test_catalog_lists_all_seeded_products(catalog):
    assert len(catalog.products()) == 12
    assert catalog.text_of(catalog.RESULT_COUNT) == "12 products"


@pytest.mark.regression
@pytest.mark.parametrize("term, expected", [
    ("keyboard", {"Mechanical Keyboard"}),
    ("KEYBOARD", {"Mechanical Keyboard"}),          # search is case-insensitive
    ("usb", {"27in 4K Monitor", "Desk Lamp"}),       # matches the description, not just the name
    ("desk", {"Desk Lamp", "Desk Plant"}),
])
def test_search_matches_name_and_description(catalog, term, expected):
    catalog.search(term)
    assert {p.name for p in catalog.products()} == expected


@pytest.mark.regression
def test_search_with_no_matches_shows_message(catalog):
    catalog.search("zzz-no-such-thing")
    assert catalog.products() == []
    assert catalog.text_of(catalog.NO_RESULTS) == "No products match your search."


@pytest.mark.regression
@pytest.mark.parametrize("category, count", [("Books", 3), ("Electronics", 4), ("Home", 3), ("Accessories", 2)])
def test_category_filter(catalog, category, count):
    catalog.search(category=category)
    products = catalog.products()
    assert len(products) == count
    for card in catalog.find_all(catalog.CARDS):
        assert category.upper() in card.text.upper()


@pytest.mark.regression
@pytest.mark.parametrize("sort, reverse", [("price_asc", False), ("price_desc", True)])
def test_sort_by_price(catalog, sort, reverse):
    catalog.search(sort=sort)
    prices = [p.price_cents for p in catalog.products()]
    assert prices == sorted(prices, reverse=reverse)


@pytest.mark.regression
def test_out_of_stock_product_cannot_be_added(catalog):
    plant = next(p for p in catalog.products() if p.name == "Desk Plant")
    assert plant.in_stock is False
    assert catalog.find_all(catalog.add_button_for("Desk Plant")) == []
