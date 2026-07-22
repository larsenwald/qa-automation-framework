# Test Execution Summary: ShopLite v1.0

**Run date:** 2026-07-21 · **Build:** `main` · **Runner:** local, headless, `pytest -n 4`

## Result: ✅ release criteria met

| Suite | Browser | Tests | Passed | Failed | Duration |
|---|---|---|---|---|---|
| UI | Chrome | 70 | 70 | 0 | 1m 12s |
| UI | Firefox | 70 | 70 | 0 | 2m 24s |
| UI | Edge | 70 | 70 | 0 | 1m 48s |
| API | n/a | 44 | 44 | 0 | 4s |
| **Total** | | **254 executions** | **254** | **0** | |

Stability: before this run, the full suite ran 3 times in a row under `-n 4` with no failures (342/342),
after the flaky-test fixes listed in [NOTES](../NOTES.md#flaky-tests-i-debugged-instead-of-adding-retries).

## Coverage by area

| Area | Test cases | Automated tests (incl. parametrized) |
|---|---|---|
| Authentication | TC-AUTH-01..08 | 17 |
| Catalog | TC-CAT-01..06 | 13 |
| Cart (incl. boundaries) | TC-CART-01..08 | 15 |
| Home page smoke | n/a | 1 |
| Checkout & orders (incl. SQL validation) | TC-CHK-01..05 | 11 |
| Browser features (alerts, frames, windows, waits) | TC-LAB-01..07 | 13 |
| API (contract, auth, validation, authorization) | TC-API-01..11 | 44 |

## Defects

| ID | Severity | Status | Regression test |
|---|---|---|---|
| BUG-001 | Major | Closed | ✅ passing |
| BUG-002 | Major | Closed | ✅ passing |
| BUG-003 | Critical | Closed | ✅ passing |
| BUG-004 | Minor | Closed | ✅ passing |

Open defects: **0**

## Not executed in this cycle
- Selenium Grid run (`docker-compose.grid.yml`): Docker not available on the run machine
- Newman run of the Postman collection: covered by the equivalent pytest API cases; runs in the CI `newman` job
- Out-of-scope items from the [test plan](TEST_PLAN.md#out-of-scope-this-release)
