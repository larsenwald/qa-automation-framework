import pytest

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
