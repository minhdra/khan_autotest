# Chạy bằng terminal (không cần giao diện web)

Không cần chạy `python -m app` hay mở trình duyệt vào GUI. Có hai công cụ dòng lệnh dùng chung bộ test case:

| Công cụ | Lệnh | Báo cáo |
|---|---|---|
| **CLI** | `python -m app.cli <file>` | `data/runs/<thời-gian>/` (HTML, XLSX, CSV, JSON, ảnh lỗi) |
| **pytest** | `python -m pytest` | bảng kết quả trên terminal, `--junitxml`, ảnh lỗi ở `data/pytest/` |

Kết quả in ra terminal từng dòng; exit code `0` = không có FAIL/ERROR, `1` = có lỗi (dùng được cho CI).

> **Windows PowerShell:** thay `.venv/bin/python` bằng `.\.venv\Scripts\python.exe`, `\` cuối dòng bằng backtick, biến môi trường dạng `$env:KHAN_HEADLESS="0"`. Xem [INSTALL.md mục 2b](INSTALL.md).

## 1. Máy thường (đã cài theo [INSTALL.md](INSTALL.md))
```bash
cd khan_autotest

# a) Headless — mặc định, không hiện cửa sổ
.venv/bin/python -m app.cli testcases/khan_full.csv
.venv/bin/python -m app.cli testcases/khan_full.csv --ids LG01,LG26,NV03      # chỉ vài test

# b) Hiện cửa sổ Firefox để nhìn tận mắt (cần màn hình / desktop)
.venv/bin/python -m app.cli testcases/khan_full.csv --ids LG01,LG26 --no-headless --delay 3

# c) Có tài khoản test (cho test dùng {EMAIL}/{PASSWORD}, login_then_open)
.venv/bin/python -m app.cli testcases/khan_full.csv --email a@b.c --password 'xxx'
```
Tùy chọn CLI: `--ids`, `--email`, `--password`, `--base-url`, `--no-headless`, `--delay` (giây nghỉ giữa test),
`--retries` (chạy lại khi ERROR).

**pytest tương đương:**
```bash
uv pip install --python .venv/bin/python -r requirements-dev.txt          # một lần
.venv/bin/python -m pytest tests/test_login.py -v                          # headless
KHAN_HEADLESS=0 KHAN_DELAY=3 .venv/bin/python -m pytest tests/test_login.py -k "LG01 or LG26" -v   # hiện cửa sổ
KHAN_EMAIL=a@b.c KHAN_PASSWORD='xxx' .venv/bin/python -m pytest            # cả bộ, có tài khoản
```

## 2. Máy chủ không có màn hình (SSH / server)
Chế độ hiện cửa sổ cần một màn hình ảo:
```bash
sudo apt install xvfb                 # một lần
xvfb-run -a .venv/bin/python -m app.cli testcases/khan_full.csv --no-headless
```
Để **xem** cửa sổ đó từ xa, dùng bản Docker (mục 3) hoặc cài x11vnc + noVNC như `docker-entrypoint.sh`.

## 3. Bản Docker, không dùng GUI
Container đã có sẵn Firefox + màn hình ảo `:99` + noVNC. Chạy lệnh trong container đang chạy:
```bash
# Headless
docker compose exec autotest python -m app.cli testcases/khan_full.csv --ids LG01,LG26

# Hiện cửa sổ trên màn hình ảo (DISPLAY=:99 bắt buộc khi dùng exec)
docker compose exec -e DISPLAY=:99 autotest \
    python -m app.cli testcases/khan_full.csv --ids LG01,LG26 --no-headless --delay 3
```
**Xem trình duyệt đang chạy:** mở http://localhost:6080/vnc.html (bấm *Connect*; nhập `VNC_PASSWORD` nếu có đặt)
trong lúc lệnh `--no-headless` đang chạy. Từ xa qua tunnel: `<url-tunnel>/vnc/vnc.html?autoconnect=1&resize=scale&path=vnc/websockify`
(cần đăng nhập Basic Auth của GUI).

Không muốn chạy trong container đang sống, dùng container tạm (không mở GUI):
```bash
docker compose run --rm --no-deps --entrypoint "" autotest \
    python -m app.cli testcases/khan_full.csv --ids LG01       # chỉ headless
```
Báo cáo nằm ở `./data/runs/<thời-gian>/` trên máy host (volume `./data`). Thư mục chạy theo giờ UTC của container.

pytest trong container: image chỉ copy `app/`, nên chạy pytest ở máy thường (mục 1) hoặc mount mã nguồn:
```bash
docker compose run --rm --no-deps --entrypoint "" -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD":/srv -w /srv autotest \
    sh -c "pip install -q -r requirements-dev.txt && python -m pytest tests/test_login.py -k LG01"
```

## 4. Đọc kết quả
```
[1/2] LG01     PASS     Hiển thị ô email/tên đăng nhập
[2/2] LG26     FAIL     Gửi form bằng phím Enter (sai thông tin)
PASS 1 | FAIL 1 | ERROR 0 | SKIPPED 0 | 50.0%
Báo cáo: data/runs/20261014_080306
```
Mở `report.html` trong thư mục báo cáo để xem chi tiết + ảnh chụp. `FAIL` = sai kết quả; `ERROR` = lỗi script/mạng;
`SKIPPED` = tắt hoặc thiếu tài khoản. Xem thêm bảng sự cố ở [USAGE.md](USAGE.md).
