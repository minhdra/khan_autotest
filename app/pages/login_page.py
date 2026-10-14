"""LoginPage: trang /login."""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class LoginPage(BasePage):
    USER = (By.ID, "username-field")
    PASS = (By.CSS_SELECTOR, "input[type=password]")
    SUBMIT = (By.CSS_SELECTOR, "[data-testid=log-in-submit-button], button[type=submit]")
    SERVER_ERR = (By.CSS_SELECTOR, "[data-testid=log-in-server-error]")
    FIELD_ERR = (By.CSS_SELECTOR, "[data-testid=identifier-error], [data-testid=password-error]")

    def load(self):
        self.open("/login")
        self.wait().until(EC.visibility_of_element_located(self.USER))

    def submit(self, email, password, use_enter=False):
        u = self.d.find_element(*self.USER)
        u.clear()
        if email:
            u.send_keys(email)
        p = self.d.find_element(*self.PASS)
        p.clear()
        if password:
            p.send_keys(password)
        if use_enter:
            p.send_keys(Keys.ENTER)
        else:
            self.js_click(self.d.find_element(*self.SUBMIT))

    def wait_result(self, t=6):
        """Chờ tới khi: rời trang login, hoặc xuất hiện lỗi từ server/field."""
        def done(d):
            if "/login" not in d.current_url:
                return True
            for el in d.find_elements(*self.SERVER_ERR):
                if el.text.strip():
                    return True
            return False
        try:
            WebDriverWait(self.d, t).until(done)
        except TimeoutException:
            pass  # lỗi field (rỗng/sai định dạng) có thể không có text -> vẫn đánh giá bình thường

    def login(self, email, password, use_enter=False):
        self.load()
        self.submit(email, password, use_enter)
        self.wait_result()
