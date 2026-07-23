# qa-automation-framework

A Selenium WebDriver + pytest test automation framework for **ShopLite**, a small e-commerce web app with a
REST API. ShopLite is included in this repo as the application under test, so the whole suite runs
offline, deterministically, and in CI.

**114 automated tests** across UI (Chrome, Firefox, Edge), REST API and SQL data checks. They found and
regression-proofed **4 real defects** in the app, all documented Jira-style in [`docs/defects/`](docs/defects/).

| | |
|---|---|
| **UI automation** | Selenium 4, Page Object Model, explicit waits only, XPath + CSS locators |
| **Browser features** | JS alerts / confirms / prompts, iframes, multiple windows & tabs, late-loading content |
| **Cross-browser** | `--browser chrome|firefox|edge`, local or on **Selenium Grid** (`--grid-url`) |
| **API testing** | `requests` + **JSON Schema** contract tests; **Postman collection** run by Newman |
| **Database validation** | SQL queries through a read-only `DbClient`, checking that what the UI says is what was saved |
| **Data-driven** | Login matrix from JSON, `parametrize` for boundaries and validation rules |
| **Reporting** | pytest-html report with **screenshot + page source on every UI failure**; JUnit XML for CI |
| **Speed** | Parallel with `pytest-xdist`; one isolated server + DB per worker (full suite in ~70 s) |
| **CI/CD** | GitHub Actions (API, Newman, 3-browser matrix, nightly) and a Jenkins declarative pipeline |
| **QA docs** | [Test plan](docs/TEST_PLAN.md), [test cases + traceability](docs/TEST_CASES.md), [defect reports](docs/defects/), [execution summary](docs/TEST_SUMMARY.md) |

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements-test.txt

pytest                          # everything, Chrome headless
pytest -n auto                  # in parallel
```

Selenium Manager downloads the right browser drivers automatically. You only need the browsers installed.

### Common runs

```bash
pytest -m smoke                                    # 9 critical-path checks, ~5 s
pytest -m ui --browser firefox --headed            # watch it in Firefox
pytest -m api                                      # REST API only, no browser
pytest -m db                                       # tests that validate data with SQL
pytest -m ui --browser edge -n 4 --html=reports/report.html --self-contained-html
```

| Option | Default | |
|---|---|---|
| `--browser` | `chrome` | `chrome`, `firefox` or `edge` |
| `--headed` | off | Show the browser window |
| `--grid-url` | none | Run on Selenium Grid, e.g. `http://localhost:4444/wd/hub` |
| `--app-host` | `host.docker.internal` | How Grid containers reach the app under test |

Markers: `smoke`, `regression`, `ui`, `api`, `db`.

### Selenium Grid

```bash
docker compose -f docker-compose.grid.yml up -d        # hub + Chrome, Firefox, Edge nodes
pytest -m ui --grid-url http://localhost:4444/wd/hub --browser firefox -n 3
```
Watch a session live at http://localhost:7900 (password `secret`).

### Postman / Newman
```bash
flask --app wsgi seed && flask --app wsgi run &
npx newman@6 run postman/ShopLite.postman_collection.json -e postman/local.postman_environment.json
```

### Run the app by itself
```bash
pip install -r requirements.txt
flask --app wsgi seed
flask --app wsgi run        # http://127.0.0.1:5000  (login: standard_user / secret_sauce)
```
Or with Docker: `docker build -t shoplite . && docker run -p 5000:5000 shoplite`.

## Defects found by the suite

| ID | Severity | Summary | Caught by |
|---|---|---|---|
| [BUG-001](docs/defects/BUG-001-login-loses-destination.md) | Major | Login drops the page the user was trying to reach | UI flow test |
| [BUG-002](docs/defects/BUG-002-login-redirects-to-post-endpoint.md) | Major | Fixing BUG-001 sent guest "Add to cart" to a **405** page (regression) | UI flow test |
| [BUG-003](docs/defects/BUG-003-cart-quantity-not-validated.md) | **Critical** | Server accepted 0/negative/over-stock quantities → **negative order totals**, checkout **500** | Boundary-value tests with client validation bypassed |
| [BUG-004](docs/defects/BUG-004-api-accepts-boolean-as-integer.md) | Minor | API accepted `"quantity": true` as 1 | API negative type tests |

The framework had its own flaky-test bugs too. How each was diagnosed (not just retried) is in [NOTES.md](NOTES.md).

## API under test

| Method | Endpoint | Auth | Notes |
|---|---|---|---|
| GET | `/api/health` | | Liveness |
| POST | `/api/auth/token` | | `{username, password}` → signed bearer token (1 h) |
| GET | `/api/products` | | `?q=` search, `?category=` filter |
| GET | `/api/products/{id}` | | 404 JSON if missing |
| GET | `/api/cart` | Bearer | Items, subtotal, 8% tax |
| POST | `/api/cart` | Bearer | `{product_id, quantity}`; 400 bad types, 422 rule violations |
| DELETE | `/api/cart/{product_id}` | Bearer | 204 / 404 |
| POST | `/api/orders` | Bearer | Address → 201 order; 422 validation; 409 empty cart / stock |
| GET | `/api/orders`, `/api/orders/{id}` | Bearer | Only the caller's own orders |

## Project layout

```
framework/                 reusable test infrastructure
  driver_factory.py        Chrome/Firefox/Edge options, local or Grid
  live_server.py           runs ShopLite in a thread on a throwaway SQLite DB
  db_client.py             read-only SQL helpers for data validation
  api_client.py            requests session with token login
pages/                     Page Object Model
  base_page.py             explicit-wait helpers, reload-aware clicks
  login_page.py  catalog_page.py  product_page.py  cart_page.py  checkout_page.py  lab_pages.py
tests/
  conftest.py              CLI options, fixtures, screenshot-on-failure hook
  data/                    JSON test data
  ui/                      Selenium tests
  api/                     API tests + JSON Schemas
postman/                   collection + environment
docs/                      test plan, test cases, defect reports, execution summary
shoplite/                  the application under test (Flask + SQLite)
.github/workflows/         GitHub Actions
Jenkinsfile                Jenkins pipeline
docker-compose.grid.yml    Selenium Grid 4
```

## Framework rules

1. **No `time.sleep`, no implicit waits.** Every wait is an explicit condition.
2. **Tests talk to page objects, page objects talk to the driver.** Locators live in one place.
3. **Every test is independent.** The DB is reseeded per test and each parallel worker has its own server.
4. **Assert the data, not just the screen.** Critical flows are checked in the database too.
5. **A flaky test is a bug.** Find the root cause; don't add retries.
