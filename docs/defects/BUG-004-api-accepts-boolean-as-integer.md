# BUG-004: `POST /api/cart` accepts JSON booleans as integers

| Field | Value |
|---|---|
| **Project** | ShopLite (SHOP) |
| **Type** | Bug |
| **Priority** | Low |
| **Severity** | Minor (bad input accepted, no crash) |
| **Status** | Closed, fixed in `Fix: reject JSON booleans for integer API fields (BUG-004)` |
| **Component** | API |
| **Found by** | `tests/api/test_orders_api.py::test_add_to_cart_rejects_bad_input` (negative type testing) |
| **Reported** | 2026-07-16 |

## Summary
`{"product_id": 2, "quantity": true}` returns **201 Created** and adds one item. `true` should be rejected
as a type error, the same way `"2"` and `1.5` already are.

## Steps to reproduce
```http
POST /api/cart
Authorization: Bearer <token>
Content-Type: application/json

{"product_id": 2, "quantity": true}
```

## Expected result
`400 {"error": "product_id and quantity must be integers"}`

## Actual result
`201 Created`. The cart contains 1 × Wireless Mouse.

## Root cause
The type check used `isinstance(value, int)`. In Python `bool` is a subclass of `int`, so `True` passes
and acts as `1`. The same applied to `product_id: true`, which resolved to product 1.

## Fix
`_is_int()` excludes `bool` explicitly. Test cases were added for both fields.
