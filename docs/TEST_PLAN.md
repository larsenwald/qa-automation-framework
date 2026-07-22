# Test Plan: ShopLite v1.0

| | |
|---|---|
| **Author** | Imrane Mariami |
| **Version** | 1.0 (2026-07-21) |
| **Application** | ShopLite web storefront + REST API (`/api`) |
| **Related** | [Test cases](TEST_CASES.md) · [Defect reports](defects/) · [Execution summary](TEST_SUMMARY.md) |

## 1. Objective
Confirm that ShopLite's core purchase flow (log in → browse → cart → checkout → order history) works
correctly on Chrome, Firefox and Edge. Also confirm that the REST API and the database stay consistent
with what the UI shows. Each regression check should run automatically on every change.

## 2. Scope

### In scope
| Area | Functional | Negative / boundary | Automated |
|---|---|---|---|
| Authentication (UI + API token) | ✔ | ✔ invalid creds, injection strings, open redirects, tampered tokens | ✔ |
| Catalog search, filter, sort | ✔ | ✔ no results, case-insensitivity | ✔ |
| Cart | ✔ | ✔ quantity boundaries (0, -1, stock, stock+1), client-validation bypass | ✔ |
| Checkout & orders | ✔ | ✔ field validation, empty cart, stock re-check | ✔ |
| Data integrity (SQL) | ✔ | ✔ order totals, line items, stock, cart clean-up | ✔ |
| REST API contract | ✔ | ✔ types, status codes, JSON Schema, auth | ✔ (pytest + Postman) |
| Browser features | ✔ alerts, iframes, windows/tabs, dynamic content | | ✔ |

### Out of scope (this release)
- Performance and load testing (the Postman collection only checks a 500 ms response time on `/health`)
- Payment processing (ShopLite has no payment gateway)
- Mobile browsers and visual regression
- Accessibility audit (planned, see [NOTES](../NOTES.md#what-id-do-next))

## 3. Test approach

| Level | Tool | What it covers |
|---|---|---|
| UI end-to-end | Selenium WebDriver 4 + pytest, Page Object Model | User flows in real browsers |
| API | `requests` + `jsonschema`; Postman/Newman | Contract, status codes, auth, validation |
| Database | SQL through `DbClient` (read-only connection) | That what the UI/API reports is what was stored |
| Manual / exploratory | Test cases in [TEST_CASES.md](TEST_CASES.md) | New features before automation, UX issues |

**Techniques used:** equivalence partitioning (valid/invalid logins, categories), boundary-value analysis
(quantity 0/1/24/25/26, ZIP length 4/5/10), negative and security-minded inputs (SQL injection, XSS strings,
open redirects, JSON type confusion), and state transitions (guest → logged in → order placed).

**Test data:** every test starts from the same seeded database (`shoplite.seed`), reset before each test.
Each pytest-xdist worker gets its own server and database file, so tests are independent and order doesn't
matter.

## 4. Environments

| Browser | Version | Mode |
|---|---|---|
| Chrome | Stable (Selenium Manager resolves the driver) | Headless locally and in CI; `--headed` to watch |
| Firefox | Stable | Same |
| Edge | Stable | Same |
| Selenium Grid 4 | `docker-compose.grid.yml` | Remote, through `--grid-url` |

CI: GitHub Actions (`.github/workflows/tests.yml`) and Jenkins (`Jenkinsfile`). Both run a smoke gate,
then API and a 3-browser UI matrix.

## 5. Entry & exit criteria

**Entry:** the build deploys, `flask seed` succeeds, and the smoke suite (`pytest -m smoke`) passes.

**Exit (release-ready):**
- 100% of smoke tests and ≥ 98% of regression tests pass on all three browsers
- No open **Critical** or **High** defects
- Every fixed defect has an automated regression test that reproduces the original failure

## 6. Defect management
Defects are written in Jira format in [`docs/defects/`](defects/) with severity, priority, steps to reproduce,
expected vs. actual results, root cause and the regression tests added. Severity scale:

| Severity | Meaning |
|---|---|
| Critical | Data corruption, money miscalculated, crash in the purchase flow |
| Major | Main flow broken or user lands on an error page; workaround exists |
| Minor | Wrong behavior with low impact |
| Trivial | Cosmetic |

## 7. Risks

| Risk | Mitigation |
|---|---|
| Flaky UI tests hide real failures | Explicit waits only (no `sleep`, no implicit waits); reload-aware clicks; root-cause fixes instead of blind retries |
| Browser/driver version drift | Selenium Manager resolves matching drivers; nightly CI run catches breakage early |
| Shared test data causing order-dependent results | Database reseeded per test; one database per worker |
| Client-side validation masking server bugs | Tests strip HTML5 constraints and also call the API directly |

## 8. Deliverables
Automation framework (this repo), HTML reports with failure screenshots, JUnit XML for CI, Postman
collection, defect reports and the [execution summary](TEST_SUMMARY.md).
