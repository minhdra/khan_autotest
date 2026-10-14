# Kiến trúc & thiết kế

## Bài toán
Kiểm thử giao diện (UI/E2E) website thật https://vi.khanacademy.org: đăng nhập (đúng/sai/biên), tìm kiếm,
điều hướng, khóa học, một số kiểm tra kỹ thuật. Yêu cầu: người không lập trình thêm/sửa test case bằng
Excel/CSV, chạy được từ GUI lẫn CI, có báo cáo, không làm hại website thật (tuần tự, có nghỉ, không sửa dữ liệu).

## Cách giải quyết
- **Data-driven:** test case là dữ liệu (CSV/XLSX/JSON), code chỉ biết một tập nhỏ *scenario* (hành động) và
  *expected_mode* (cách kiểm tra). Thêm test = thêm dòng, không đụng code.
- **Page Object Model:** mọi locator và thao tác trình duyệt nằm trong `app/pages/`; engine/tests chỉ gọi API trang.
- **Tách "làm gì" và "so sánh":** `Runner.perform` (engine/runner.py) thực hiện scenario qua page object, `Evaluator.check` (engine/assertions.py) so sánh.
- **Chống flaky:** explicit wait (implicit = 0), retry riêng cho ERROR, tách FAIL (sai kết quả) với ERROR (lỗi hạ tầng).

## Cấu trúc thư mục
```
khan_autotest/
├── app/                      # mã nguồn
│   ├── pages/                # Page Objects: locator + hành động, KHÔNG assertion
│   │   ├── base_page.py  login_page.py  search_page.py
│   ├── engine/               # engine chạy test case dữ liệu (GUI/CLI dùng)
│   │   ├── runner.py         #   Runner: driver, retry, ảnh lỗi, scenario → page object
│   │   └── assertions.py     #   Evaluator.check: toàn bộ kiểm tra
│   ├── core/                 # hạ tầng: config.py, driver.py, testcases.py (load/validate)
│   ├── reporting/report.py   # JSON/CSV/XLSX/HTML
│   ├── web/                  # server.py (HTTP, auth, /vnc proxy), jobs.py, static/ (GUI)
│   ├── cli.py                # chạy CI
│   └── __main__.py           # python -m app → GUI
├── tests/                    # pytest: chỉ chứa assertion, theo module
│   ├── conftest.py           #   ≈ BaseTest: fixtures runner/khan, tài khoản, nghỉ, ảnh lỗi
│   └── test_login.py  test_search.py  test_navigation.py  test_course.py  test_security.py
├── testcases/                # dữ liệu test (CSV/XLSX/JSON) — nguồn chung cho GUI/CLI/pytest
├── tools/gen_testcases.py    # sinh khan_full.{csv,xlsx}
├── docs/  AGENT.md  README.md
└── Dockerfile  docker-compose.yml  docker-entrypoint.sh  requirements*.txt  pytest.ini
```
Tương đương mẫu Java `src/main/java/pages` + `src/test/java/tests`: `app/pages/` ↔ pages, `tests/` ↔ tests,
`tests/conftest.py` ↔ `BaseTest`. Khác biệt: một dòng test case = một test (parametrize), nên `test_login.py` là
một hàm chạy cho mọi dòng module "Đăng nhập", không phải mỗi test một method.

## Hai cách chạy, cùng một nguồn dữ liệu
| | GUI / CLI | pytest |
|---|---|---|
| Vào bằng | `python -m app` / `python -m app.cli` | `python -m pytest` |
| Điều phối | `engine.Runner.run()` | pytest + `tests/conftest.py` |
| Hành động | `Runner.perform()` → `pages/` | cùng `Runner.perform()` |
| Kiểm tra | `Evaluator.check` | cùng `Evaluator.check`, nằm trong `assert` |
| Báo cáo | `report.write_all` (HTML/XLSX/…) | báo cáo pytest (thêm `--junitxml`) |

## Sơ đồ luồng
```
 GUI ─► web/server.py ─► web/jobs.py ─┐
 CLI ─► cli.py ───────────────────────┼─► engine/runner.py ─► pages/* ─► core/driver.py (Firefox)
 pytest ─► tests/conftest.py ─────────┘          │
                                                  └─► engine/assertions.py ; reporting/report.py
 core/testcases.py ── đọc testcases/*.csv|xlsx|json ──► tất cả
```

| File | Vai trò |
|---|---|
| `app/core/config.py` | đường dẫn (`data/`, `testcases/`, `data/runs/`) + `DEFAULTS` |
| `app/core/testcases.py` | `load()` → list dict; `validate()`; `SCENARIOS`, `MODES` |
| `app/core/driver.py` | `make_driver()` Firefox, vi-VN, implicit wait 0, page-load 60s |
| `app/pages/` | Page Objects (xem dưới) |
| `app/engine/runner.py` | `Runner.perform()` (scenario → page), `run_one()` (retry, FAIL/ERROR), `run()` |
| `app/engine/assertions.py` | `Evaluator.check`, `norm` |
| `app/web/jobs.py` | `JobManager`: chạy nền, trạng thái cho GUI poll, `history()` |
| `app/web/server.py` | HTTP server stdlib + auth + proxy noVNC |
| `app/reporting/report.py` | `summarize()` + `write_all()` |
| `docker-entrypoint.sh` | khởi Xvfb + x11vnc + websockify(noVNC) rồi chạy app |

## Page Object Model
- `BasePage`: `open()` (+ gỡ banner cookie TrustArc), `wait()`, `body_text()`, `main_text()`, `js_click()`, và API
  cho runner/assertions: `url`, `title`, `is_visible(css)`, `click_css(css)`, `pause(s)`, `screenshot(path)`.
- `LoginPage`: `login()`, `submit(use_enter)`, `wait_result()`; `SearchPage`: `search()`, `result_count()`.
- **Quy tắc:** `engine/` và `tests/` không import `By`/`expected_conditions`, không gọi `driver.find_element*`.
  Trang mới → file mới trong `app/pages/` kế thừa `BasePage`, export ở `pages/__init__.py`, thêm scenario ở
  `Runner.perform` + `core/testcases.SCENARIOS`.

## Thuật toán chạy một test case (`Runner.run_one`)
1. `enabled=0` → `SKIPPED`. Cần credential (`login_then_open`, `{EMAIL}`, `{PASSWORD}`) mà thiếu → `SKIPPED`.
2. Thay placeholder; lặp `retries+1` lần: tạo driver (lazy, dùng chung cả phiên), `_execute(tc)` → `(ok, page)`.
3. `ok` → `PASS`; không → `FAIL` + ảnh chụp. Exception → `ERROR` + trace + ảnh; thử lại; nếu chụp ảnh cũng lỗi → reset driver.
4. `actual` = 300 ký tự đầu của `<main>`, `url` = URL cuối; mật khẩu thật không bao giờ ghi vào kết quả
   (giữ nguyên placeholder `{PASSWORD}`).
5. Giữa các test nghỉ `delay` giây (trừ SKIPPED).

**So khớp văn bản:** chuẩn hóa NFC + lower (site có thể trả tiếng Việt dạng NFD); `expected` tách bằng `|` thành các
phương án OR.

**Chờ kết quả đăng nhập:** thoát khỏi `/login` hoặc xuất hiện text lỗi server; timeout 6s thì vẫn đánh giá
(lỗi field có thể không có text). **Chờ tìm kiếm:** có `.gsc-result` hoặc thông báo "không khớp"/"did not match".

## Luồng GUI
`POST /api/run` → `JobManager.start` (khóa, nạp + validate, tạo `data/runs/<id>/`, thread nền) → GUI poll
`GET /api/status` (`status`, `done/total`, `results[]`) → xong thì `report.write_all` → `GET /runs/<id>/<file>`.
Chỉ một phiên chạy tại một thời điểm (vì dùng chung một Firefox và để không dồn tải lên site).

## Bảo mật
- Basic Auth (`hmac.compare_digest`) áp dụng cho mọi route, gồm `/runs/*` và `/vnc/*`. Không đặt → mở tự do (chỉ nội bộ).
- `/runs/` chống path traversal (`resolve()` + kiểm tra nằm trong `RUNS_DIR`); tên file upload qua regex `SAFE`.
- Public qua Cloudflare quick tunnel chỉ phơi cổng 8765; noVNC được proxy qua `/vnc/` (HTTP + WebSocket raw pipe)
  nên dùng chung auth thay vì mở cổng 6080.

## Hạn chế đã biết
- Google CSE (tìm kiếm) có thể hiện reCAPTCHA khi chạy dày → test `search`/`results_min` FAIL giả; tăng `delay`.
- Selector và nội dung phụ thuộc giao diện thật của Khan Academy → có thể vỡ khi site đổi; sửa tại `app/pages/`/CSV.
- Quick tunnel: URL đổi sau mỗi lần khởi động, không SLA. Cần URL cố định → named tunnel.
- Một phiên một lúc; không chạy song song; chỉ Firefox.
- Server stdlib `ThreadingHTTPServer`, không phù hợp tải lớn (đủ cho công cụ nội bộ).
