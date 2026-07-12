"""Builds WebDriver instances for Chrome, Firefox and Edge, locally or on a Selenium Grid.

Selenium Manager (bundled with Selenium 4.6+) resolves the matching driver binaries,
so nothing needs to be downloaded by hand.
"""
from selenium import webdriver

SUPPORTED_BROWSERS = ("chrome", "firefox", "edge")
WINDOW_SIZE = (1366, 900)


# Chromium pops a "save password?" / "password found in a data breach" bubble after a form
# login. It swallows the next click, so tests that log in first would randomly do nothing.
CHROMIUM_PREFS = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
}


def _chrome_options(headless):
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("prefs", CHROMIUM_PREFS)
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return opts


def _edge_options(headless):
    opts = webdriver.EdgeOptions()
    opts.add_experimental_option("prefs", CHROMIUM_PREFS)
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}")
    opts.add_argument("--disable-gpu")
    return opts


def _firefox_options(headless):
    opts = webdriver.FirefoxOptions()
    if headless:
        opts.add_argument("-headless")
    opts.add_argument(f"--width={WINDOW_SIZE[0]}")
    opts.add_argument(f"--height={WINDOW_SIZE[1]}")
    return opts


OPTIONS = {"chrome": _chrome_options, "firefox": _firefox_options, "edge": _edge_options}
LOCAL = {"chrome": webdriver.Chrome, "firefox": webdriver.Firefox, "edge": webdriver.Edge}


def create_driver(browser="chrome", headless=True, grid_url=None):
    browser = browser.lower()
    if browser not in SUPPORTED_BROWSERS:
        raise ValueError(f"Unsupported browser {browser!r}; pick one of {SUPPORTED_BROWSERS}")

    options = OPTIONS[browser](headless)
    if grid_url:
        driver = webdriver.Remote(command_executor=grid_url, options=options)
    else:
        driver = LOCAL[browser](options=options)

    if browser == "firefox":
        driver.set_window_size(*WINDOW_SIZE)
    # Explicit waits only. An implicit wait mixed with explicit waits makes timeouts unpredictable.
    driver.implicitly_wait(0)
    driver.set_page_load_timeout(30)
    return driver
