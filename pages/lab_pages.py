"""Page objects for the lab pages: alerts, iframes, windows and late-loading content."""
from contextlib import contextmanager

from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class AlertsPage(BasePage):
    path = "/lab/alerts"

    ALERT_BTN = (By.ID, "js-alert")
    CONFIRM_BTN = (By.ID, "js-confirm")
    PROMPT_BTN = (By.ID, "js-prompt")
    RESULT = (By.ID, "result")

    def trigger(self, button) -> Alert:
        self.click(button)
        return self.wait().until(EC.alert_is_present())

    @property
    def result(self):
        return self.text_of(self.RESULT)


class FramesPage(BasePage):
    path = "/lab/frames"

    HEADING = (By.ID, "frames-heading")
    FRAME = (By.ID, "chat-frame")
    CHAT_INPUT = (By.ID, "chat-input")
    CHAT_SEND = (By.ID, "chat-send")
    BOT_MESSAGES = (By.CSS_SELECTOR, "#messages .bot")

    @contextmanager
    def inside_chat(self):
        """Switch into the iframe for the block, and *always* switch back out."""
        self.wait().until(EC.frame_to_be_available_and_switch_to_it(self.FRAME))
        try:
            yield self
        finally:
            self.driver.switch_to.default_content()

    def send_message(self, text):
        before = len(self.find_all(self.BOT_MESSAGES))
        self.type(self.CHAT_INPUT, text)
        self.click(self.CHAT_SEND)
        # The bot replies after a delay; wait for a new message rather than sleeping.
        self.wait().until(lambda d: len(self.find_all(self.BOT_MESSAGES)) > before)
        return self.find_all(self.BOT_MESSAGES)[-1].text


class WindowsPage(BasePage):
    path = "/lab/windows"

    NEW_TAB_LINK = (By.ID, "policy-tab")
    POPUP_BUTTON = (By.ID, "policy-popup")
    POLICY_HEADING = (By.ID, "policy-heading")
    RETURN_DAYS = (By.ID, "return-days")

    def open_and_switch(self, trigger):
        """Click something that opens a window and switch to it. Returns the original handle."""
        original = self.driver.current_window_handle
        known = set(self.driver.window_handles)
        self.click(trigger)
        self.wait().until(EC.number_of_windows_to_be(len(known) + 1))
        new_handle = (set(self.driver.window_handles) - known).pop()
        self.driver.switch_to.window(new_handle)
        self.wait_for_url_contains("/lab/windows/policy")
        return original


class DynamicPage(BasePage):
    path = "/lab/dynamic"

    LOAD_BTN = (By.ID, "load-recs")
    SPINNER = (By.ID, "spinner")
    REC_ITEMS = (By.CSS_SELECTOR, "#recs .rec-item")
    CLAIM_BTN = (By.ID, "claim-deal")
    DEAL_STATUS = (By.ID, "deal-status")

    def load_recommendations(self, timeout=10):
        self.click(self.LOAD_BTN)
        self.wait(timeout).until(EC.invisibility_of_element_located(self.SPINNER))
        self.wait(timeout).until(lambda d: len(self.find_all(self.REC_ITEMS)) == 3)
        return [el.text for el in self.find_all(self.REC_ITEMS)]
