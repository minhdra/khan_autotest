"""Điều phối chạy test case (vòng đời driver, retry, ảnh chụp lỗi). Hành động → pages/, kiểm tra → assertions."""
import threading
import time
import traceback
from datetime import datetime

from ..core import config
from ..core.driver import make_driver
from ..pages import BasePage, LoginPage, SearchPage
from .assertions import Evaluator


class Runner:
    def __init__(self, settings, testcases, run_dir, on_update=None):
        self.s = {**config.DEFAULTS, **settings}
        self.tcs = testcases
        self.run_dir = run_dir
        self.shots = run_dir / "screenshots"
        self.shots.mkdir(parents=True, exist_ok=True)
        self.on_update = on_update or (lambda *_: None)
        self.results = []
        self._stop = threading.Event()
        self.driver = None

    def stop(self):
        self._stop.set()

    # -- một test case ------------------------------------------------------
    def _sub(self, v):
        return v.replace("{EMAIL}", self.s.get("email", "")).replace("{PASSWORD}", self.s.get("password", ""))

    def perform(self, tc):
        """Thực hiện scenario bằng page object, trả về page ở trạng thái cuối (chưa kiểm tra)."""
        base, to = self.s["base_url"], self.s["timeout"]
        d = self.driver
        sc = tc["scenario"]
        in1, in2 = self._sub(tc["input1"]), self._sub(tc["input2"])
        if sc in ("login", "login_enter"):
            page = LoginPage(d, base, to)
            page.login(in1, in2, use_enter=(sc == "login_enter"))
        elif sc == "click":
            page = BasePage(d, base, to)
            page.open(in1 or "/")
            page.click_css(tc["input2"])
            page.pause(2)
        elif sc == "login_then_open":
            page = LoginPage(d, base, to)
            page.login(self.s.get("email", ""), self.s.get("password", ""))
            if "/login" in page.url:
                raise RuntimeError("Đăng nhập không thành công, không thể mở trang tiếp theo")
            page.open(in1 or "/")
            page.pause(2)
        elif sc == "search":
            page = SearchPage(d, base, to)
            page.search(in1)
        elif sc == "open_page":
            page = BasePage(d, base, to)
            page.open(in1 or "/")
            page.pause(1.5)
        else:
            raise ValueError(f"scenario không hợp lệ: {sc}")
        return page

    def _execute(self, tc):
        page = self.perform(tc)
        return Evaluator.check(tc["expected_mode"], tc["expected"], page), page

    def needs_creds(self, tc):
        blob = tc["input1"] + tc["input2"]
        return tc["scenario"] == "login_then_open" or "{EMAIL}" in blob or "{PASSWORD}" in blob

    def run_one(self, tc):
        res = {"id": tc["id"], "module": tc["module"], "title": tc["title"], "type": tc["type"], "priority": tc["priority"],
               "scenario": tc["scenario"], "input1": tc["input1"],
               "input2": tc["input2"],  # placeholder {PASSWORD} giữ nguyên, không lộ mật khẩu thật
               "expected": f"{tc['expected_mode']}: {tc['expected']}",
               "status": "", "actual": "", "url": "", "error": "", "screenshot": "", "duration": 0.0,
               "attempts": 0, "started": datetime.now().strftime("%H:%M:%S")}
        t0 = time.time()
        if not tc.get("enabled", True):
            res.update(status="SKIPPED", error="Bị tắt (enabled=0)")
            return res
        if self.needs_creds(tc) and not (self.s.get("email") and self.s.get("password")):
            res.update(status="SKIPPED", error="Cần email/mật khẩu tài khoản (nhập ở phần Cài đặt)")
            return res
        attempts = int(self.s["retries"]) + 1
        for n in range(1, attempts + 1):
            res["attempts"] = n
            try:
                if self.driver is None:
                    self.driver = make_driver(self.s["headless"], self.s["window"], self.s["timeout"])
                ok, page = self._execute(tc)
                res["status"] = "PASS" if ok else "FAIL"
                res["error"] = "" if ok else "Kết quả thực tế không khớp expected"
                res["actual"] = " ".join(page.main_text().split())[:300]
                res["url"] = page.url
                if not ok:
                    self._shot(res, tc)
                break
            except Exception as e:  # lỗi script / mạng / không tìm thấy phần tử
                res["status"] = "ERROR"
                res["error"] = f"{type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}"
                res["trace"] = traceback.format_exc()
                try:
                    res["url"] = self.driver.current_url if self.driver else ""
                    self._shot(res, tc)
                except Exception:
                    self._reset_driver()
        res["duration"] = round(time.time() - t0, 2)
        return res

    def _shot(self, res, tc):
        name = f"{tc['id']}.png"
        BasePage(self.driver, self.s["base_url"]).screenshot(self.shots / name)
        res["screenshot"] = f"screenshots/{name}"

    def _reset_driver(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass
        self.driver = None

    # -- cả bộ --------------------------------------------------------------
    def run(self):
        try:
            for i, tc in enumerate(self.tcs, 1):
                if self._stop.is_set():
                    break
                self.on_update("start", tc, i, len(self.tcs))
                r = self.run_one(tc)
                self.results.append(r)
                self.on_update("done", r, i, len(self.tcs))
                if r["status"] not in ("SKIPPED",) and i < len(self.tcs):
                    time.sleep(float(self.s["delay"]))
        finally:
            self._reset_driver()
