"""SearchPage: trang /search (kết quả do Google CSE render)."""
import time
import unicodedata

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class SearchPage(BasePage):
    BOX = (By.CSS_SELECTOR, "[data-testid=page-search-box], input[type=text]")

    def load(self):
        self.open("/search")
        self.wait().until(EC.visibility_of_element_located(self.BOX))

    def search(self, query):
        """Gõ từ khóa vào ô tìm kiếm rồi Enter (đúng luồng người dùng); rỗng thì chỉ Enter."""
        self.load()
        box = self.d.find_element(*self.BOX)
        box.clear()
        if query:
            box.send_keys(query)
        box.send_keys(Keys.ENTER)
        time.sleep(1)
        # kết quả do Google CSE render: chờ có kết quả hoặc thông báo không khớp
        def ready(d):
            t = unicodedata.normalize("NFC", self.main_text()).lower()
            return ("không khớp" in t) or d.find_elements(By.CSS_SELECTOR, ".gsc-webResult, .gsc-result") \
                or "did not match" in t
        try:
            WebDriverWait(self.d, self.timeout).until(ready)
        except TimeoutException:
            pass

    def result_count(self):
        return len(self.d.find_elements(By.CSS_SELECTOR, ".gsc-webResult.gsc-result"))
