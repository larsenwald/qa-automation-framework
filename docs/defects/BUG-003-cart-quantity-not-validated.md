# BUG-003: Server accepts zero, negative and over-stock cart quantities

| Field | Value |
|---|---|
| **Project** | ShopLite (SHOP) |
| **Type** | Bug |
| **Priority** | Highest |
| **Severity** | Critical (negative order totals are possible; checkout crashes with 500) |
| **Status** | Closed, fixed in `Fix: validate cart quantity against stock on the server (BUG-003)` |
| **Component** | Cart / Checkout / API |
| **Environment** | All browsers; also reproducible through `POST /api/cart` |
| **Found by** | `tests/ui/test_quantity_boundaries.py` (boundary-value analysis) |
| **Reported** | 2026-07-13 |

## Summary
The quantity field only has HTML5 `min="1"` validation. Once that is bypassed (DevTools, a script, or the
API), the server accepts any integer:

| Input | Result |
|---|---|
| `0` | Row with quantity 0 added to the cart |
| `-3` on a $89.99 item | Cart subtotal becomes **-$234.98** |
| `9999` (stock 25) | Item added. **Checkout then fails with HTTP 500** (`sqlite3.IntegrityError: CHECK constraint failed: stock >= 0`) |
| `20`, then `10` more (stock 25) | 30 in the cart, more than exists |

## Steps to reproduce (UI)
1. Log in as `standard_user`.
2. Open `/product/1` (Mechanical Keyboard, stock 25).
3. In DevTools, remove the `min` attribute from `#quantity`, enter `-3` and click **Add to cart**.
4. Open the cart. The subtotal is negative.

## Steps to reproduce (API)
```http
POST /api/cart
Authorization: Bearer <token>
{"product_id": 1, "quantity": -5}
```
→ `201 Created`

## Expected result
Quantities outside `1..(stock - already in cart)` are rejected with a clear message, and nothing is
written to `cart_items`.

## Root cause
- No server-side check on `quantity`. The UI route used `request.form.get(type=int)`, which also quietly
  turns `"abc"` into the default `1`.
- The UI and the API each had their own copy of the insert logic.
- Checkout trusted the cart and only the DB `CHECK` constraint stopped overselling, which showed up as a 500.

## Fix
- New `shop.add_item()` is the single validated path for both the UI and `POST /api/cart`
  (→ `422` with a message).
- Checkout re-checks stock before placing the order (stock can change after the item was added), and
  `POST /api/orders` returns `409 Insufficient stock`.

## Regression tests added
- `test_valid_quantities_are_accepted[1, 2, 24, 25]`: boundaries just inside the range
- `test_invalid_quantities_are_rejected[0, -1, -50, 26, 9999]`: boundaries just outside, plus extremes
- `test_cart_total_cannot_exceed_stock_across_adds`
- Each one checks the database (`cart_items`), not just the UI message.
