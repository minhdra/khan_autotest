# Cài đặt

## 1. Bản Docker (khuyến nghị)
Image gồm sẵn Firefox ESR, geckodriver, Xvfb + x11vnc + noVNC; không cần cài gì thêm trên máy.

**Yêu cầu:** Docker + Docker Compose v2.

```bash
cd khan_autotest
# (tùy chọn) tạo file .env theo mẫu bên dưới trước khi chạy
docker compose up -d --build
```
Mở http://localhost:8765.

`.env` (tùy chọn):
```
AUTH_USER=admin          # Basic Auth cho giao diện — BẮT BUỘC đặt khi public qua tunnel
AUTH_PASS=<mật-khẩu-mạnh>
VNC_PASSWORD=<mật-khẩu>  # mật khẩu màn hình noVNC (để trống = không mật khẩu)
```
Không commit `.env` (đã nằm trong `.gitignore`).

| Mục | Giá trị |
|---|---|
| Cổng 8765 | giao diện web + API (+ proxy noVNC tại `/vnc/`) |
| Cổng 6080 | noVNC trực tiếp (chỉ dùng trong mạng nội bộ) |
| `./data` → `/data` | báo cáo + ảnh chụp lỗi (`data/runs/<thời-gian>/`) |
| `./testcases` → `/srv/testcases` | sửa/thêm file test case ngay trên máy, không cần build lại |
| service `tunnel` | Cloudflare quick tunnel → `http://autotest:8765` |

Lấy URL public: `docker compose logs tunnel | grep trycloudflare` (URL đổi mỗi lần tunnel khởi động lại).
Không muốn public: `docker compose up -d autotest` (không chạy service `tunnel`).

Cập nhật sau khi sửa code: `docker compose up -d --build autotest`.
Kiến trúc CPU amd64/arm64 đều được (Dockerfile tự chọn geckodriver).

## 2. Bản chạy thường (không Docker)
**Yêu cầu:** Python ≥ 3.10, Firefox, geckodriver (nếu thiếu, Selenium Manager sẽ cố tự tải).

```bash
cd khan_autotest
uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt
# hoặc: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python -m app                       # GUI: http://127.0.0.1:8765
.venv/bin/python -m app.cli testcases/khan_full.csv --email a@b.c --password '***'   # CLI
```
Biến môi trường (đều tùy chọn):

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `HOST` / `PORT` | `127.0.0.1` / `8765` | địa chỉ lắng nghe của GUI |
| `AUTOTEST_DATA` | `./data` | nơi lưu báo cáo |
| `AUTOTEST_TESTCASES` | `./testcases` | thư mục test case |
| `GECKODRIVER` | tự tìm trong PATH | đường dẫn geckodriver |
| `AUTH_USER` / `AUTH_PASS` | trống (không auth) | Basic Auth cho GUI |
| `VNC_PORT` | trống | nếu có, GUI hiện link "Xem trình duyệt trực tiếp" (chỉ có ý nghĩa khi có Xvfb/noVNC) |

Chạy ở chế độ "Hiện cửa sổ" (không headless) cần có màn hình thật hoặc Xvfb.

## Cài thêm để chạy pytest (tùy chọn)
```bash
uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/python -m pytest tests/test_login.py -k LG01
```

## Kiểm tra cài đặt
```bash
.venv/bin/python -m app.cli testcases/testcases.csv --ids LG01 --delay 0   # kỳ vọng: PASS 1
```
