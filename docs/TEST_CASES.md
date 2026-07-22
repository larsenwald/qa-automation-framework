# Test Cases: ShopLite

Priority: **P1** = smoke / release blocker, **P2** = regression, **P3** = nice to have.
"Automated by" points to the pytest test that covers the case, which serves as the traceability matrix.

## Authentication

| ID | Title | Pri | Steps | Expected | Automated by |
|---|---|---|---|---|---|
| TC-AUTH-01 | Valid login | P1 | Open `/login`, enter `standard_user` / `secret_sauce`, submit | Redirected to catalog; header shows username; "Welcome back" flash | `ui/test_login.py::test_valid_login` |
| TC-AUTH-02 | Invalid credentials | P1 | Submit wrong password / unknown user / empty fields | "Invalid username or password." shown; not logged in | `test_invalid_login_is_rejected` (8 data rows) |
| TC-AUTH-03 | Injection strings in login | P2 | Username `' OR '1'='1' --` and `<script>` | Rejected like any bad login; no error page | `test_invalid_login_is_rejected[sql-injection, script-tag]` |
| TC-AUTH-04 | Password masked | P3 | Inspect password field | `type="password"` | `test_password_field_is_masked` |
| TC-AUTH-05 | Logout ends session | P1 | Log in, click Log out, open `/cart` | Redirected to login | `test_logout_ends_session` |
| TC-AUTH-06 | Return to requested page | P2 | Logged out, open `/orders`, log in | Lands on `/orders` | `test_protected_page_returns_user_after_login` (BUG-001) |
| TC-AUTH-07 | No open redirect | P1 | `/login?next=https://evil.example`, log in | Stays on ShopLite (`/`) | `test_login_ignores_external_next_url` (3 variants) |
| TC-AUTH-08 | Guest add-to-cart flow | P2 | Logged out, click Add to cart, log in | Logged in on catalog, no 405 | `ui/test_cart.py::test_anonymous_add_to_cart_goes_to_login_then_catalog` (BUG-002) |

## Catalog

| ID | Title | Pri | Steps | Expected | Automated by |
|---|---|---|---|---|---|
| TC-CAT-01 | All products listed | P1 | Open `/` | 12 cards, "12 products" | `test_catalog_lists_all_seeded_products` |
| TC-CAT-02 | Search name & description, case-insensitive | P2 | Search `keyboard`, `KEYBOARD`, `usb`, `desk` | Matching products only | `test_search_matches_name_and_description` |
| TC-CAT-03 | No results | P2 | Search nonsense | "No products match your search." | `test_search_with_no_matches_shows_message` |
| TC-CAT-04 | Category filter | P2 | Pick each category | Only that category, correct count | `test_category_filter` |
| TC-CAT-05 | Sort by price | P2 | Sort low→high and high→low | Prices are in order | `test_sort_by_price` |
| TC-CAT-06 | Out of stock | P2 | Find Desk Plant | "Out of stock", no add button | `test_out_of_stock_product_cannot_be_added` |

## Cart

| ID | Title | Pri | Steps | Expected | Automated by |
|---|---|---|---|---|---|
| TC-CART-01 | Add item | P1 | Add Wireless Mouse | Badge = 1; cart line qty 1; subtotal $29.99 | `test_add_to_cart_updates_badge_and_cart` |
| TC-CART-02 | Same item twice | P2 | Add Sticker Pack twice | One line, qty 2 | `test_adding_same_item_twice_increments_quantity` |
| TC-CART-03 | Subtotal | P1 | Add 3 different items | Subtotal = sum of lines | `test_subtotal_is_sum_of_line_totals` |
| TC-CART-04 | Remove item | P2 | Remove only item | "Your cart is empty."; badge 0 | `test_remove_item_empties_cart` |
| TC-CART-05 | Quantity from product page | P2 | Qty 3 on product page | Cart line qty 3 | `test_add_multiple_from_product_page` |
| TC-CART-06 | Quantity, valid boundaries | P2 | Qty 1, 2, 24, 25 (stock 25) | Accepted | `ui/test_quantity_boundaries.py::test_valid_quantities_are_accepted` |
| TC-CART-07 | Quantity, invalid boundaries (client validation bypassed) | P1 | Remove `min` attr; qty 0, -1, -50, 26, 9999 | Rejected with message; nothing in DB | `test_invalid_quantities_are_rejected` (BUG-003) |
| TC-CART-08 | Cumulative stock limit | P2 | Add 20 then 10 (stock 25) | Second add rejected | `test_cart_total_cannot_exceed_stock_across_adds` |

## Checkout & orders

| ID | Title | Pri | Steps | Expected | Automated by |
|---|---|---|---|---|---|
| TC-CHK-01 | End-to-end purchase + DB check | P1 | Keyboard + Clean Code → checkout → valid address | Confirmation; totals $124.98 + $10.00 tax = $134.98; DB order, items, stock -1, cart empty | `ui/test_checkout.py::test_end_to_end_purchase_is_saved_correctly` |
| TC-CHK-02 | Field validation | P1 | Blank name, bad emails, blank address, ZIP 4 / 9+4 / letters | Field-level error; no order row in DB | `test_checkout_field_validation` (7 rows) |
| TC-CHK-03 | Sticky form values | P3 | Submit with bad ZIP | Other fields keep their values | `test_checkout_keeps_entered_values_after_error` |
| TC-CHK-04 | Empty cart | P2 | Open `/checkout` with empty cart | Redirect to cart with message | `test_empty_cart_cannot_checkout` |
| TC-CHK-05 | Order history | P2 | Place order, open `/orders` | Order listed | `test_order_shows_in_history` |

## Browser features (lab)

| ID | Title | Pri | Expected | Automated by |
|---|---|---|---|---|
| TC-LAB-01 | alert() | P2 | Text read, accepted, result shown | `ui/test_lab.py::test_simple_alert_text_and_accept` |
| TC-LAB-02 | confirm() accept/dismiss | P2 | "Cart cleared" / "Kept items" | `test_confirm_dialog` |
| TC-LAB-03 | prompt() input / cancel | P2 | Coupon applied, rejected, cancelled | `test_prompt_dialog`, `test_prompt_cancel` |
| TC-LAB-04 | iframe interaction | P2 | Chat reply read inside frame; main page usable after | `test_chat_widget_inside_iframe` |
| TC-LAB-05 | New tab & popup | P2 | Switch, verify, close, return to original | `test_policy_opens_in_new_window` |
| TC-LAB-06 | Late-loading content | P2 | Waits for random 0.8–2.3 s delay without sleep | `test_recommendations_load_after_random_delay` |
| TC-LAB-07 | Disabled → enabled button | P3 | Clickable after countdown | `test_flash_sale_button_enables_after_countdown` |

## API

| ID | Title | Pri | Expected | Automated by |
|---|---|---|---|---|
| TC-API-01 | Health | P1 | 200 `{"status":"ok"}` | `api/test_products_api.py::test_health`, Postman |
| TC-API-02 | Product list contract | P1 | Matches JSON Schema; count == items | `test_list_products_matches_schema`, Postman |
| TC-API-03 | API ↔ DB consistency | P2 | Price & stock equal DB for every SKU | `test_product_list_matches_database` |
| TC-API-04 | Filters | P2 | Correct counts/categories | `test_filter_products` |
| TC-API-05 | 404 as JSON | P2 | 404 + `{"error"}` | `test_unknown_product_returns_404_json` |
| TC-API-06 | SQL injection in search | P1 | 200, 0 results, table intact | `test_sql_injection_in_search_is_harmless` |
| TC-API-07 | Token auth | P1 | Valid → token; bad/missing/tampered → 401 | `api/test_auth_api.py` |
| TC-API-08 | Cart input validation | P1 | 0/neg/over-stock → 422; wrong types (incl. `true`) → 400; unknown → 404 | `api/test_orders_api.py::test_add_to_cart_rejects_bad_input` (BUG-003, BUG-004) |
| TC-API-09 | Order end-to-end + DB | P1 | 201; totals & stock correct in DB; cart cleared | `test_place_order_end_to_end`, Postman |
| TC-API-10 | Order validation / empty cart | P2 | 422 with field name / 409 | `test_order_validation_errors`, `test_order_with_empty_cart_conflicts` |
| TC-API-11 | Authorization between users | P1 | Other user's order → 404 | `test_users_cannot_see_each_others_orders` |
