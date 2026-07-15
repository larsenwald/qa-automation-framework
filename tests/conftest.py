import re
from pathlib import Path

import pytest

try:
    import pytest_html
except ImportError:  # the HTML report is optional
    pytest_html = None

from framework.db_client import DbClient
from framework.driver_factory import SUPPORTED_BROWSERS, create_driver
from framework.live_server import LiveServer
from pages.login_page import LoginPage


def pytest_addoption(parser):
    group = parser.getgroup("shoplite")
    group.addoption("--browser", default="chrome", choices=SUPPORTED_BROWSERS,
                    help="Browser to run UI tests in (default: chrome)")
    group.addoption("--headed", action="store_true", help="Show the browser window")
    group.addoption("--grid-url", default=None, help="Selenium Grid URL, e.g. http://localhost:4444")


ARTIFACTS = Path("reports")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On a failed UI test: save a screenshot + page source and embed the screenshot in the HTML report."""
    outcome = yield
    report = outcome.get_result()
    driver = item.funcargs.get("driver")
    if report.when != "call" or not report.failed or driver is None:
        return

    safe_name = re.sub(r"[^\w.-]+", "_", item.nodeid)[-150:]
    shots = ARTIFACTS / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)
    png = shots / f"{safe_name}.png"
    try:
        driver.save_screenshot(str(png))
        (shots / f"{safe_name}.html").write_text(driver.page_source, encoding="utf-8")
        report.sections.append(("failure context", f"URL: {driver.current_url}\nScreenshot: {png}"))
        if pytest_html is not None:
            extras = getattr(report, "extras", [])
            extras.append(pytest_html.extras.image(driver.get_screenshot_as_base64(), "Screenshot"))
            extras.append(pytest_html.extras.url(driver.current_url, "Page URL"))
            report.extras = extras
    except Exception as exc:  # a dead browser shouldn't hide the real failure
        report.sections.append(("failure context", f"could not capture screenshot: {exc}"))


def pytest_html_report_title(report):
    report.title = "ShopLite automation report"


@pytest.fixture(scope="session")
def live_server(tmp_path_factory):
    server = LiveServer(tmp_path_factory.mktemp("db") / "shoplite.sqlite").start()
    yield server
    server.stop()


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server.url


@pytest.fixture(scope="session")
def db(live_server):
    return DbClient(live_server.db_path)


@pytest.fixture(autouse=True)
def clean_data(live_server):
    """Every test starts from the same seeded data, so order of execution never matters."""
    live_server.reset_data()


@pytest.fixture
def driver(request):
    opts = request.config.option
    drv = create_driver(opts.browser, headless=not opts.headed, grid_url=opts.grid_url)
    yield drv
    drv.quit()


@pytest.fixture
def logged_in(driver, base_url):
    """A browser already signed in as the standard demo user."""
    LoginPage(driver, base_url).login_as("standard_user", "secret_sauce")
    return driver
