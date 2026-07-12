# BUG-002: Guest "Add to cart" ends on a 405 Method Not Allowed page after login

| Field | Value |
|---|---|
| **Project** | ShopLite (SHOP) |
| **Type** | Bug (regression, introduced by the BUG-001 fix) |
| **Priority** | High |
| **Severity** | Major (user lands on an error page during the purchase flow) |
| **Status** | Closed, fixed in `Fix: don't use POST-only URLs as the post-login redirect (BUG-002)` |
| **Component** | Auth / Cart |
| **Environment** | Chrome, Firefox, Edge (all reproduce) |
| **Found by** | `tests/ui/test_cart.py::test_anonymous_add_to_cart_goes_to_login_then_catalog` |
| **Reported** | 2026-07-12 |

## Summary
When a logged-out user clicks **Add to cart**, they are sent to `/login?next=/cart/add/2`. After logging in,
the browser does a `GET /cart/add/2`, but that route only accepts `POST`, so the user sees
**405 Method Not Allowed**.

## Steps to reproduce
1. Start logged out and open the catalog (`/`).
2. Click **Add to cart** on *Wireless Mouse*.
3. On the login page, sign in as `standard_user` / `secret_sauce`.

## Expected result
The user is logged in and lands on a working page (the catalog), with a prompt to continue shopping.

## Actual result
`GET /cart/add/2` → **405 Method Not Allowed**.

Server log:
```
POST /cart/add/2                    302
GET  /login?next=/cart/add/2        200
POST /login?next=/cart/add/2        302
GET  /cart/add/2                    405
```

## Root cause
The BUG-001 fix recorded `request.full_path` as `next` for *every* request, including form POSTs. A
redirect is always followed with GET, so a POST-only URL can never be a valid "return to" target.

## Fix
`login_required` only records `next` for `GET` requests. For anything else the user goes to the catalog
after login. A flash message ("Please log in to continue.") now explains the redirect.

## Lessons
The BUG-001 regression test only covered a GET page (`/orders`). Redirect logic needs at least one test
per HTTP method that can hit the decorator.
