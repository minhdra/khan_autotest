"""BasePage: thao tác chung cho mọi trang (mở, chờ, click, đọc text, ảnh chụp)."""
import time

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, base_url, timeout=15):
        self.d = driver
        self.base = base_url.rstrip("/")
        self.timeout = timeout

    def wait(self, t=None):
        return WebDriverWait(self.d, t or self.timeout)

    def open(self, path="/"):
        url = path if path.startswith("http") else self.base + (path if path.startswith("/") else "/" + path)
        self.d.get(url)
        self.dismiss_cookie_banner()

    def dismiss_cookie_banner(self):
        """Banner TrustArc che các nút bên dưới -> bấm 'Strictly Necessary Only', không được thì gỡ khỏi DOM."""
        try:
            btn = WebDriverWait(self.d, 3).until(EC.element_to_be_clickable((By.ID, "truste-consent-required")))
            btn.click()
            time.sleep(0.5)
        except (TimeoutException, WebDriverException):
            pass
        try:
            self.d.execute_script("var b=document.getElementById('truste-consent-track'); if(b) b.remove();")
        except WebDriverException:
            pass

    def body_text(self):
        try:
            return self.d.find_element(By.TAG_NAME, "body").text
        except WebDriverException:
            return ""

    def main_text(self):
        try:
            return self.d.find_element(By.TAG_NAME, "main").text
        except WebDriverException:
            return self.body_text()

    def js_click(self, el):
        try:
            el.click()
        except WebDriverException:
            self.d.execute_script("arguments[0].click();", el)

    # -- API cho Evaluator / Runner: không để lộ driver & locator ra ngoài page --
    @property
    def url(self):
        return self.d.current_url

    @property
    def title(self):
        return self.d.title

    def pause(self, seconds):
        time.sleep(seconds)

    def is_visible(self, css):
        """True nếu có ít nhất một phần tử khớp CSS selector đang hiển thị."""
        return any(e.is_displayed() for e in self.d.find_elements(By.CSS_SELECTOR, css))

    def click_css(self, css):
        """Chờ phần tử bấm được rồi bấm (JS click nếu bị che)."""
        el = self.wait().until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
        self.js_click(el)

    def screenshot(self, path):
        self.d.save_screenshot(str(path))
