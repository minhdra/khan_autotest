# Khan Academy AutoTest

Bộ kiểm thử tự động giao diện cho **https://vi.khanacademy.org** bằng Selenium WebDriver (Firefox) + Python,
theo mô hình **Page Object Model**, **data-driven** (test case nằm trong CSV/XLSX/JSON), có giao diện web để chạy
và báo cáo HTML/Excel/CSV/JSON.

| Tài liệu | Nội dung |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | Cài đặt: bản Docker và bản chạy thường |
| [docs/RUN_TERMINAL.md](docs/RUN_TERMINAL.md) | Chạy chỉ bằng terminal (CLI/pytest), headless hoặc hiện cửa sổ, kể cả trong Docker |
| [docs/USAGE.md](docs/USAGE.md) | Hướng dẫn dùng: giao diện web, CLI, viết test case, đọc báo cáo, public qua tunnel |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | Phương pháp kiểm thử: phạm vi, kỹ thuật thiết kế test case, trạng thái kết quả, chống flaky, quy trình |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Kiến trúc, luồng chạy, thuật toán, API, định dạng báo cáo, hạn chế |
| [AGENT.md](AGENT.md) | Bản tóm tắt cho AI agent khác: cần biết gì trước khi sửa code |

## Chạy nhanh
**Docker:** `docker compose up -d --build` → mở http://localhost:8765
**Thường:** `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt && .venv/bin/python -m app`
(cần Firefox + geckodriver). **Windows PowerShell:** xem [mục 2b](docs/INSTALL.md) (không dùng `&&`, venv ở `.venv\Scripts\`). Chi tiết ở [docs/INSTALL.md](docs/INSTALL.md).

## Lưu ý production
Đây là website thật của bên thứ ba: chạy tuần tự, nghỉ giữa các test (mặc định 2s), chỉ đọc / đăng nhập thử,
không có test thêm/xóa dữ liệu tài khoản. Chạy nhiều lần tìm kiếm liên tục có thể bị Google CSE hiện captcha
(xem mục Hạn chế trong ARCHITECTURE).
