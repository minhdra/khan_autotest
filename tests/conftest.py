"""BaseTest dạng pytest: vòng đời trình duyệt, tài khoản, nghỉ giữa test, ảnh chụp khi lỗi.

Biến môi trường: KHAN_BASE_URL, KHAN_EMAIL, KHAN_PASSWORD, KHAN_HEADLESS(=1), KHAN_DELAY(=2), KHAN_PATH(file test case).
Test file chỉ chứa assertion; hành động nằm ở app/pages/ (qua Runner.perform).
"""
import os
import time
from pathlib import Path

import pytest

from app.core import config, testcases
from app.engine import Runner

CASE_FILE = Path(os.environ.get("KHAN_TESTCASES", config.TESTCASE_DIR / "khan_full.csv"))
SHOTS = config.DATA_DIR / "pytest"


def cases_for(module):
    """Các test case của một module trong file test case, dùng cho parametrize."""
    return [t for t in testcases.load(CASE_FILE) if t["module"] == module]


@pytest.fixture(scope="session")
def settings():
    return {
        "base_url": os.environ.get("KHAN_BASE_URL", config.DEFAULTS["base_url"]),
        "headless": os.environ.get("KHAN_HEADLESS", "1") != "0",
        "delay": float(os.environ.get("KHAN_DELAY", config.DEFAULTS["delay"])),
        "email": os.environ.get("KHAN_EMAIL", ""),
        "password": os.environ.get("KHAN_PASSWORD", ""),
    }


@pytest.fixture(scope="session")
def runner(settings, tmp_path_factory):
    r = Runner(settings, [], tmp_path_factory.mktemp("run"))
    yield r
    r._reset_driver()


@pytest.fixture
def khan(runner, settings, request):
    """Trả về hàm khan(tc) -> page (đã thực hiện scenario). Tự skip theo enabled/credential."""
    def perform(tc):
        if not tc.get("enabled", True):
            pytest.skip("enabled=0")
        if runner.needs_creds(tc) and not (settings["email"] and settings["password"]):
            pytest.skip("cần KHAN_EMAIL/KHAN_PASSWORD")
        if runner.driver is None:
            from app.core.driver import make_driver
            runner.driver = make_driver(settings["headless"], runner.s["window"], runner.s["timeout"])
        page = runner.perform(tc)
        request.node.page = page
        return page
    yield perform
    time.sleep(settings["delay"])  # không dồn request lên production


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    out = yield
    rep = out.get_result()
    page = getattr(item, "page", None)
    if rep.when == "call" and rep.failed and page is not None:
        SHOTS.mkdir(parents=True, exist_ok=True)
        try:
            page.screenshot(SHOTS / f"{item.name.replace('/', '_')}.png")
        except Exception:
            pass
