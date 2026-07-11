# BUG-001: Login does not return the user to the page they were trying to open

| Field | Value |
|---|---|
| **Project** | ShopLite (SHOP) |
| **Type** | Bug |
| **Priority** | Medium |
| **Severity** | Major (broken user flow, no data loss) |
| **Status** | Closed, fixed in `Fix: return to requested page after login` |
| **Component** | Auth |
| **Environment** | Chrome 1xx / Firefox 1xx / Edge 1xx, headless, local ShopLite build |
| **Found by** | `tests/ui/test_login.py::test_protected_page_returns_user_after_login` |
| **Reported** | 2026-07-11 |

## Summary
A logged-out user who opens a protected page (for example `/orders`) is sent to `/login`, but after a
successful login they land on the catalog (`/`) instead of the page they asked for.

## Steps to reproduce
1. Log out (or start a new session).
2. Go to `http://localhost:5000/orders`.
3. You are redirected to `/login`. Log in as `standard_user` / `secret_sauce`.

## Expected result
The user is redirected to `/orders`.

## Actual result
The user is redirected to `/`. The original destination is lost.

## Root cause
`login_required` redirected to `url_for("auth.login")` without recording where the user came from,
and `login()` always redirected to the catalog.

## Fix
- `login_required` now passes the requested path as `?next=`.
- `login()` follows `next` **only if** it is a same-site relative path (`safe_next()`). Absolute URLs,
  protocol-relative `//host` and backslash tricks (`/\host`) are ignored, so the fix doesn't open an
  **open-redirect** hole.

## Regression tests added
- `test_protected_page_returns_user_after_login`
- `test_login_ignores_external_next_url[https://evil.example | //evil.example | /\\evil.example]`
