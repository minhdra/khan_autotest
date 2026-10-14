# Hướng dẫn sử dụng

## 1. Giao diện web
1. Chọn **file test case** (danh sách lấy từ thư mục `testcases/`) hoặc tải file mới lên (.csv/.xlsx/.json).
2. Tick các test case muốn chạy (mặc định tất cả).
3. **Cài đặt:** base URL, email/mật khẩu tài khoản test (chỉ cần cho test dùng `{EMAIL}`/`{PASSWORD}` hoặc
   `login_then_open`; không được lưu vào file), nghỉ giữa test, timeout, số lần thử lại, headless / "Hiện cửa sổ".
4. Bấm **Chạy**; theo dõi tiến độ và kết quả từng dòng. Bấm **Dừng** để dừng sau test case hiện tại.
5. Tải báo cáo (HTML/XLSX/CSV/JSON hoặc `all.zip`) ở mục Lịch sử. Có file mẫu: `/api/template`.
6. "Xem trình duyệt trực tiếp ↗" (khi bật "Hiện cửa sổ"): xem Firefox đang chạy theo thời gian thực qua noVNC.

## 2. Dòng lệnh / CI
> Hướng dẫn đầy đủ không cần web (headless / hiện cửa sổ / Docker): [RUN_TERMINAL.md](RUN_TERMINAL.md).

```bash
python -m app.cli <file> [--ids LG01,LG02] [--email E --password P] [--base-url URL]
                         [--no-headless] [--delay 2.0] [--retries 1]
```
Exit code `0` nếu không có FAIL/ERROR, `1` nếu có. Báo cáo ở `data/runs/<thời-gian>/`.

## 2b. Chạy bằng pytest
```bash
uv pip install --python .venv/bin/python -r requirements-dev.txt
KHAN_EMAIL=a@b.c KHAN_PASSWORD='***' .venv/bin/python -m pytest              # cả bộ
.venv/bin/python -m pytest tests/test_login.py -k "LG01 or LG26"             # chọn test
.venv/bin/python -m pytest --junitxml=data/pytest/junit.xml                  # cho CI
```
Mỗi file `tests/test_<module>.py` chạy các dòng của module tương ứng trong `testcases/khan_full.csv`
(đổi file bằng `KHAN_TESTCASES`). Biến: `KHAN_BASE_URL`, `KHAN_EMAIL`, `KHAN_PASSWORD`, `KHAN_HEADLESS=0`,
`KHAN_DELAY` (giây nghỉ giữa test). Ảnh chụp khi lỗi: `data/pytest/`. Test cần tài khoản sẽ tự `skip` nếu thiếu.

## 3. Viết test case
Một dòng = một test case. Cột:
`id, module, title, type, priority, scenario, input1, input2, expected_mode, expected, note, enabled`

**scenario** (hành động):

| scenario | input1 | input2 |
|---|---|---|
| `open_page` | đường dẫn, vd `/math` | – |
| `login` | email | mật khẩu (bấm nút Đăng nhập) |
| `login_enter` | email | mật khẩu (gửi form bằng phím Enter) |
| `login_then_open` | trang cần mở sau khi đăng nhập (dùng tài khoản ở Cài đặt) | – |
| `click` | trang cần mở | CSS selector phần tử cần bấm |
| `search` | từ khóa (rỗng = chỉ Enter) | – |

**expected_mode** (kiểm tra) — dùng `|` để OR nhiều giá trị, so khớp NFC + không phân biệt hoa/thường:

| expected_mode | expected |
|---|---|
| `url_contains` / `url_not_contains` | chuỗi trong URL |
| `text_contains` / `text_not_contains` | chuỗi trong nội dung trang |
| `title_contains` | chuỗi trong tiêu đề tab |
| `element_visible` | CSS selector phải hiển thị |
| `results_min` | số kết quả tìm kiếm tối thiểu |

`enabled`: `0/no/false` để bỏ qua. `{EMAIL}`/`{PASSWORD}` trong input được thay bằng tài khoản ở Cài đặt/CLI.
`id` để trống thì tự đánh `TC001…`; ID phải duy nhất. Sinh lại bộ đầy đủ: `python tools/gen_testcases.py`.

**Trạng thái kết quả:** `PASS` | `FAIL` (kết quả khác expected, có ảnh chụp) | `ERROR` (lỗi script/mạng/không tìm
thấy phần tử; có thể `retries`) | `SKIPPED` (tắt, hoặc thiếu tài khoản).

## 4. Public qua tunnel
Compose có service `tunnel` (Cloudflare quick tunnel). Trước khi public **bắt buộc** đặt `AUTH_USER/AUTH_PASS`.
Chỉ cổng 8765 ra ngoài; noVNC đi qua `/vnc/` của chính server (cùng Basic Auth).
Lấy URL: `docker compose logs tunnel | grep trycloudflare`. Muốn URL mới: `docker restart <tên container tunnel>`.

## 5. Xử lý sự cố
| Hiện tượng | Cách xử lý |
|---|---|
| Test tìm kiếm FAIL, trang hiện "xác nhận bạn không phải rô-bốt" | Google CSE giới hạn tốc độ; tăng `delay`, chạy lại sau ít phút |
| `ERROR: SessionNotCreated…` | thiếu/lệch Firefox–geckodriver; dùng Docker hoặc cài lại |
| "Xem trình duyệt trực tiếp" lỗi qua tunnel | cần bản có proxy `/vnc/` (đã có từ 2026-10-13); rebuild image |
| Test đăng nhập bị SKIPPED | chưa nhập email/mật khẩu ở Cài đặt |
