"""Chạy dòng lệnh (CI):  python -m app.cli testcases/testcases.csv --email x --password y"""
import argparse
import sys
from datetime import datetime

from .core import config, testcases
from .engine import Runner
from .reporting import report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--ids", help="ID cách nhau dấu phẩy")
    ap.add_argument("--email", default="")
    ap.add_argument("--password", default="")
    ap.add_argument("--base-url", default=config.DEFAULTS["base_url"])
    ap.add_argument("--no-headless", action="store_true")
    ap.add_argument("--delay", type=float, default=config.DEFAULTS["delay"])
    ap.add_argument("--retries", type=int, default=0)
    a = ap.parse_args()
    tcs = testcases.load(a.file)
    errs = testcases.validate(tcs)
    if errs:
        sys.exit("\n".join(errs))
    if a.ids:
        want = set(a.ids.split(","))
        tcs = [t for t in tcs if t["id"] in want]
    run_dir = config.RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    st = {"base_url": a.base_url, "headless": not a.no_headless, "delay": a.delay, "retries": a.retries,
          "email": a.email, "password": a.password}

    def show(kind, item, i, n):
        if kind == "done":
            print(f"[{i}/{n}] {item['id']:<8} {item['status']:<8} {item['title']}", flush=True)

    r = Runner(st, tcs, run_dir, show)
    r.run()
    meta = {"started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "file": a.file, "base_url": a.base_url,
            "browser": "Firefox"}
    s = report.write_all(run_dir, meta, r.results)
    print(f"\nPASS {s['pass']} | FAIL {s['fail']} | ERROR {s['error']} | SKIPPED {s['skipped']} "
          f"| {s['pass_rate']}%\nBáo cáo: {run_dir}")
    sys.exit(0 if s["fail"] + s["error"] == 0 else 1)


if __name__ == "__main__":
    main()
