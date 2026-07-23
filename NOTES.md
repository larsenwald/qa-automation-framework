# Notes: design decisions, bugs, and what I learned

## Why test my own app instead of a public demo site?
Public practice sites change, go down, or rate-limit, and you can't check their database. With ShopLite in
the repo I control the data (reseeded before every test), I can **validate with SQL**, and CI is fully
deterministic. It also meant the bugs I found were real, so I had to write proper defect reports, fix them,
and prove the fixes with regression tests, like a real QA/dev loop.

## Framework design decisions

**Page Object Model.** Locators and page actions live in `pages/`, and tests read like steps
(`catalog.search(category="Books")`). When the HTML changes, one file changes.

**Explicit waits only.** `driver.implicitly_wait(0)` is set on purpose: mixing implicit and explicit waits
makes timeouts add up unpredictably. Every wait in `BasePage` is a condition (visible, clickable, text
present, stale, alert present, window count).

**Reload-aware clicks.** `click_and_wait_for_reload()` grabs the old `<html>` element, clicks, and waits for
it to go stale. Without it, the next lookup can hit the *old* page (`StaleElementReferenceException`).

**Locator strategy.** IDs first (fast, stable), CSS for structure (`tr.cart-row[data-sku='KB-001']`),
XPath when I need to walk *up* the tree. `CatalogPage.add_button_for(name)` finds a product name, goes up
to its card with `ancestor::`, then down to the button. CSS can't go up.

**Test isolation.** The database is reseeded before every test. The live server is session-scoped, which
under pytest-xdist means **one server + one SQLite file per worker**, so parallel tests never share state.

**Assert the data, not just the screen.** The end-to-end test checks the confirmation page and then
queries `orders`, `order_items`, `products.stock` and `cart_items`. `DbClient` opens SQLite with
`mode=ro`, so tests can't accidentally change data behind the app's back.

**Bypassing client-side validation.** `ProductPage.bypass_client_validation()` removes the HTML5 `min`
attribute with `execute_script`. That's how BUG-003 showed up: the browser blocked bad input, the server
didn't.

**API contract tests.** JSON Schemas in `tests/api/schemas.py` (with `additionalProperties: false` on
products) catch renamed, retyped or dropped fields, not just wrong values.

## Bugs found in the app
Full write-ups are in `docs/defects/`.

1. **BUG-001: login forgot where you were going.** Fixed with `?next=`, but `next` is user input, so I
   added `safe_next()` to reject `https://evil`, `//evil` and `/\evil`. Otherwise the fix would have been an
   **open redirect**. I added tests for all three variants.
2. **BUG-002: my fix caused a regression.** A guest clicking *Add to cart* (a POST) got
   `next=/cart/add/2`. After login, the redirect does a GET on it → **405**. Lesson: the BUG-001 test only
   covered a GET page. Redirect logic needs a test per HTTP method. Now `next` is only recorded for GETs.
3. **BUG-003: no server-side quantity validation (Critical).** A quantity of `-3` gave a **negative
   subtotal (-$234.98)**, and `9999` crashed checkout with a 500 (the DB `CHECK stock >= 0` was the only
   guard). The UI and the API also had duplicated insert logic. Fix: one validated `add_item()` used by
   both, plus a stock re-check at checkout, because stock can change after something is added to the cart.
   Found with boundary-value analysis: 0/1/24/25/26 around a stock of 25.
4. **BUG-004: `{"quantity": true}` accepted.** In Python `bool` is a subclass of `int`, so
   `isinstance(True, int)` is `True`. Found by negative type testing.

## Flaky tests I debugged (instead of adding retries)

- **Stale elements after search.** `products()` read the old cards before the reload. → Added
  `click_and_wait_for_reload()`.
- **Clicks that randomly did nothing after login.** No POST reached the server at all. My first guess was
  a layout shift from Tailwind's CDN styling the page late, so I added a "page styled" wait. It didn't fully
  help (still about 1 in 8 failed), so I backed it out. The pattern was that it only happened *after a form
  login*: Chrome's **password manager / leaked-password bubble** was eating the next click. Fixed by
  disabling it with Chromium prefs (`credentials_enable_service`, `password_manager_leak_detection`) for
  Chrome and Edge. Lesson: when the first theory doesn't fully fix it, revert it and look for the pattern.
- **Parallel-only failure: "Node with given id does not belong to the document".** This only showed up
  under `-n 4` load. ChromeDriver sometimes raises a generic `WebDriverException` instead of
  `StaleElementReferenceException` for an element from a document that was just replaced, and
  `EC.staleness_of` doesn't catch that. Wrote `is_stale()` to treat that specific message as stale. After
  that, 3 consecutive full parallel runs passed (342/342).
- **Edge driver download failed** on Selenium 4.27 because its Selenium Manager used Microsoft's retired
  `azureedge.net` driver URL. Upgraded to Selenium 4.45.

## Trade-offs / known limitations
- SQLite is fine for a demo but would need Postgres and real concurrency testing in production.
- The app uses Tailwind's Play CDN, which is fine for a demo. A real build would compile CSS.
- No CSRF tokens on ShopLite's forms. It's a test target, but I'd add Flask-WTF in a real app and test
  that forms without a token are rejected.
- Grid support exists (`docker-compose.grid.yml`, `--grid-url`), but my day-to-day runs were local.

## What I'd do next
- **Accessibility:** axe-core injected through `execute_script`, failing on serious violations.
- **Visual regression** on key pages (screenshot diff with a tolerance).
- **Performance smoke:** k6 or Locust against `/api/products` and checkout.
- **Allure reports** with steps and history trends, and Slack notification on nightly failures.
- **Jira integration:** create or update a ticket automatically when a nightly test fails twice in a row.
- **BDD layer** (pytest-bdd) for a few flows so business analysts can read and review scenarios.
