# AGENT.md — hướng dẫn cho AI agent làm việc với repo này

**Dự án:** Selenium (Firefox) + Python 3.12 UI test cho https://vi.khanacademy.org, POM, data-driven, GUI web + CLI.
Ngôn ngữ giao diện/chú thích/tài liệu: **tiếng Việt**. App chạy không cần framework web (stdlib + selenium + openpyxl); pytest chỉ là lớp chạy thay thế (requirements-dev.txt).

## Bản đồ nhanh
- `app/pages/` — Page Objects, mỗi trang một file. **Mọi locator/thao tác Selenium ở đây.**
- `app/engine/runner.py` — `Runner.perform` (scenario → page), `run_one` (retry, FAIL/ERROR); `app/engine/assertions.py` — `Evaluator.check`.
- `app/core/` — `config.py`, `driver.py`, `testcases.py` (`SCENARIOS`, `MODES`, `load`, `validate` = nguồn sự thật).
- `app/web/` — `server.py` (HTTP + auth + `/vnc/` proxy), `jobs.py`, `static/` (GUI); `app/reporting/report.py` — báo cáo.
- `tests/` — pytest: `conftest.py` (BaseTest) + `test_<module>.py` chỉ chứa assertion, parametrize từ `testcases/khan_full.csv`.
- `testcases/*.csv|xlsx` — dữ liệu test; `tools/gen_testcases.py` sinh `khan_full.*`.
- Chạy bằng terminal: [docs/RUN_TERMINAL.md](docs/RUN_TERMINAL.md).
- Chi tiết: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), cách dùng: [docs/USAGE.md](docs/USAGE.md), cài đặt: [docs/INSTALL.md](docs/INSTALL.md).

## Quy tắc khi sửa
1. **POM:** không dùng `By`, `EC`, `find_element*`, `time.sleep` trong `app/engine/`, `app/web/`, `tests/`. Thêm hàm vào page object.
2. **Thêm scenario:** (a) `testcases.SCENARIOS`, (b) nhánh trong `Runner.perform` (engine/runner.py), (c) cập nhật `docs/USAGE.md`.
   **Thêm expected_mode:** `testcases.MODES` + `Evaluator.check` (engine/assertions.py) + docs. Ba nơi phải đồng bộ.
3. **Phân biệt FAIL/ERROR:** FAIL = chạy được nhưng sai kết quả; ERROR = exception. Đừng nuốt exception thành FAIL.
4. **Không ghi mật khẩu thật** vào kết quả/báo cáo/log (giữ `{PASSWORD}`); không commit `.env`.
5. **Production site:** không thêm test ghi/xóa dữ liệu tài khoản; giữ tuần tự + `delay`.
6. So khớp text luôn qua `norm()` (NFC + lower).
7. `/runs/*` và upload phải giữ kiểm tra path/regex; mọi route mới phải đi sau `_authorized()`.

## Lệnh hay dùng
```bash
.venv/bin/python -m app                                   # GUI :8765
.venv/bin/python -m app.cli testcases/testcases.csv --ids LG01 --delay 0   # smoke test
docker compose up -d --build autotest                     # build + chạy bản Docker
docker compose logs tunnel | grep trycloudflare           # URL public
python tools/gen_testcases.py                             # sinh lại bộ test đầy đủ
.venv/bin/python -m pytest tests/test_login.py -q         # bản pytest (cần requirements-dev.txt)
```
Chưa có unit test cho chính framework; xác minh bằng smoke test CLI / pytest (cần Internet) — ít nhất chạy một test cho mỗi scenario đã sửa.

## Bẫy đã biết
- Tìm kiếm qua Google CSE có thể hiện captcha → `SR*` FAIL giả (không phải lỗi code). Xem actual: "xác nhận … rô-bốt".
- Banner cookie TrustArc che nút; `BasePage.open()` đã gỡ — đừng bỏ.
- Trong Docker, link noVNC phải đi qua `/vnc/…&path=vnc/websockify` (index.html tự chọn); cổng 6080 không có trên tunnel.
- Quick tunnel đổi URL mỗi lần restart; không hard-code URL.
- `data/`, `.venv/` không thuộc mã nguồn (đã ignore).
