from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "#login-form button[type='submit']")
    ERROR = (By.XPATH, "//p[@id='login-error']")

    def login(self, username, password):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)
        return self

    def login_as(self, username, password):
        """Open the login page, sign in and wait until the header shows the user."""
        self.open().login(username, password)
        self.wait_for_text(self.CURRENT_USER, username)
        return self

    @property
    def error_message(self):
        return self.text_of(self.ERROR)

    def has_error(self):
        return self.is_visible(self.ERROR)
