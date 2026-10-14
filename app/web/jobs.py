"""Quản lý một phiên chạy (chạy nền) + lịch sử."""
import json
import threading
from datetime import datetime

from ..core import config, testcases
from ..engine import Runner
from ..reporting import report


class JobManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.runner = None
        self.state = {"status": "idle", "run_id": None, "current": None, "done": 0, "total": 0, "results": [],
                      "message": ""}

    def start(self, file, ids, settings):
        with self.lock:
            if self.state["status"] == "running":
                raise RuntimeError("Đang có phiên chạy khác")
            path = config.TESTCASE_DIR / file
            tcs = testcases.load(path)
            errs = testcases.validate(tcs)
            if errs:
                raise ValueError("; ".join(errs[:5]))
            if ids:
                tcs = [t for t in tcs if t["id"] in set(ids)]
            if not tcs:
                raise ValueError("Không có test case nào được chọn")
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_dir = config.RUNS_DIR / run_id
            run_dir.mkdir(parents=True)
            self.meta = {"run_id": run_id, "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "file": file,
                         "base_url": settings.get("base_url", config.DEFAULTS["base_url"]),
                         "browser": "Firefox" + (" (headless)" if settings.get("headless", True) else "")}
            self.runner = Runner(settings, tcs, run_dir, self._on_update)
            self.state = {"status": "running", "run_id": run_id, "current": None, "done": 0,
                          "total": len(tcs), "results": [], "message": ""}
            threading.Thread(target=self._run, daemon=True).start()
            return run_id

    def _on_update(self, kind, item, i, n):
        with self.lock:
            if kind == "start":
                self.state["current"] = f"{item['id']} – {item['title']}"
            else:
                self.state["results"].append(item)
                self.state["done"] = i

    def _run(self):
        try:
            self.runner.run()
            msg = ""
        except Exception as e:
            msg = f"Lỗi nghiêm trọng: {e}"
        results = self.runner.results
        summ = report.write_all(self.runner.run_dir, self.meta, results)
        with self.lock:
            stopped = self.runner._stop.is_set()
            self.state.update(status="stopped" if stopped else ("error" if msg else "finished"),
                              current=None, message=msg, summary=summ)

    def stop(self):
        if self.runner:
            self.runner.stop()

    def snapshot(self):
        with self.lock:
            return json.loads(json.dumps(self.state, default=str))


def history():
    out = []
    for d in sorted(config.RUNS_DIR.iterdir(), reverse=True):
        f = d / "results.json"
        if f.exists():
            j = json.loads(f.read_text(encoding="utf-8"))
            out.append({"run_id": d.name, **j["meta"], "summary": j["summary"]})
    return out
