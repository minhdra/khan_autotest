"""Khởi tạo Selenium WebDriver (Firefox)."""
import os
import shutil

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def make_driver(headless=True, window="1366x900", timeout=15):
    opts = Options()
    if headless:
        opts.add_argument("-headless")
    opts.set_preference("intl.accept_languages", "vi-VN, vi")
    gecko = os.environ.get("GECKODRIVER") or shutil.which("geckodriver")
    service = Service(gecko) if gecko else Service()  # không có -> Selenium Manager tự tải
    drv = webdriver.Firefox(options=opts, service=service)
    w, h = (int(x) for x in window.lower().split("x"))
    drv.set_window_size(w, h)
    drv.set_page_load_timeout(60)
    drv.implicitly_wait(0)  # chỉ dùng explicit wait
    return drv
