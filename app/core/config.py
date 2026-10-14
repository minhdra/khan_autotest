"""Cấu hình chung cho framework."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.environ.get("AUTOTEST_DATA", ROOT / "data"))
TESTCASE_DIR = Path(os.environ.get("AUTOTEST_TESTCASES", ROOT / "testcases"))
RUNS_DIR = DATA_DIR / "runs"

DEFAULTS = {
    "base_url": "https://vi.khanacademy.org",
    "headless": True,
    "delay": 2.0,          # giây nghỉ giữa các test case (tránh dồn request lên production)
    "timeout": 15,         # explicit wait (giây)
    "retries": 0,          # chạy lại khi gặp ERROR (lỗi script/mạng), không áp dụng cho FAIL
    "window": "1366x900",
}

for _d in (DATA_DIR, RUNS_DIR, TESTCASE_DIR):
    _d.mkdir(parents=True, exist_ok=True)
