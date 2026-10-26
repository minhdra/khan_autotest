# Phương pháp kiểm thử

Tài liệu này mô tả **cách thiết kế và đánh giá test case** của bộ khan_autotest (khác với
[ARCHITECTURE.md](ARCHITECTURE.md) là mô tả code chạy thế nào).

## 1. Phạm vi và nguyên tắc
- **Đối tượng:** website thật https://vi.khanacademy.org (production, bên thứ ba), kiểm thử ở mức giao diện (UI/E2E)
  bằng Selenium + Firefox. Kiểm thử hộp đen: chỉ dựa vào những gì người dùng thấy (URL, tiêu đề, văn bản, phần tử hiển thị).
- **An toàn với production:** chỉ đọc hoặc đăng nhập thử. Không có test tạo/sửa/xóa dữ liệu tài khoản. Chạy tuần tự,
  nghỉ `delay` giây giữa các test (mặc định 2s). Các email/mật khẩu trong test âm tính là dữ liệu giả, không tồn tại.
- **Dữ liệu tách khỏi code:** một dòng CSV/XLSX/JSON = một test case. Thêm/sửa test không cần sửa code
  (trừ khi cần *scenario* hoặc *expected_mode* mới).

## 2. Bộ test hiện có (`testcases/khan_full.csv`, 83 test case)
| Module | Tiền tố ID | Số TC | Nội dung |
|---|---|---|---|
| Đăng nhập | `LG` | 31 | giao diện form, đăng nhập sai/rỗng/biên, Enter, SQLi/XSS, đăng nhập đúng |
| Tìm kiếm | `SR` | 24 | từ khóa hợp lệ/rỗng/đặc biệt/dài, số kết quả tối thiểu |
| Điều hướng | `NV` | 17 | mở các trang công khai, tiêu đề, phần tử chính |
| Khóa học / Tiến độ | `CR` | 6 | sau đăng nhập: khóa học, tiến độ, hồ sơ, cài đặt (cần tài khoản) |
| Bảo mật & kỹ thuật | `SC` | 5 | HTTPS, `type=password`, `robots.txt`, không lộ mật khẩu trên URL |

Theo loại (cột `type`): Functional 25 · Negative 14 · UI 13 · Equivalence 12 · Security 10 · Boundary 9.
Theo ưu tiên: High 27 · Medium 29 · Low 27. 8 test cần tài khoản thật (`login_then_open`, `{EMAIL}`, `{PASSWORD}`),
thiếu tài khoản thì tự `SKIPPED`. `testcases/testcases.csv` (27 dòng, ít cột hơn) là bộ smoke test nhỏ.

Bộ đầy đủ được **sinh bằng `python tools/gen_testcases.py`** (nguồn sự thật là script này, không sửa tay
`khan_full.*`; sửa script rồi sinh lại để CSV và XLSX luôn đồng bộ).

## 3. Kỹ thuật thiết kế test case
| Kỹ thuật | Áp dụng ở đâu (ví dụ) |
|---|---|
| **Phân vùng tương đương** (`Equivalence`) | mật khẩu chỉ chữ / chỉ số / chỉ ký tự đặc biệt; email viết hoa; tên đăng nhập không có `@` |
| **Phân tích giá trị biên** (`Boundary`) | mật khẩu 7 / 8 / 12 / 13 ký tự; email dài 250 ký tự |
| **Kiểm thử âm tính** (`Negative`) | để trống email/mật khẩu, thiếu `@`, có dấu cách trong email |
| **Kiểm thử bảo mật cơ bản** (`Security`) | chuỗi SQLi và XSS ở ô nhập, HTTPS, mật khẩu không lên URL |
| **Kiểm thử giao diện** (`UI`) | form có đủ ô/nút/liên kết, tiêu đề tab |
| **Kiểm thử chức năng** (`Functional`) | tìm kiếm ra kết quả, đăng nhập đúng, Enter gửi form |

Mỗi test case có `priority` (High/Medium/Low) để chọn bộ chạy nhanh (chạy High trước), và `type` để thống kê.
Quy ước ID: tiền tố module + số thứ tự hai chữ số (`LG01`…); ID duy nhất trong file.

## 4. Mô hình một test case
`scenario` (làm gì) + `input1/input2` (dữ liệu) → `expected_mode` + `expected` (so sánh với cái gì).
Danh sách scenario và expected_mode đầy đủ ở [USAGE.md mục 3](USAGE.md). Ba điểm cần nhớ:
- Hầu hết kiểm tra đăng nhập sai là **"ở lại `/login`"** (`url_contains /login`) hoặc **"có thông báo lỗi"**
  (`text_contains` với các phương án OR, như `không đúng|incorrect`), vì site có thể đổi câu chữ thông báo.
- `expected` dùng `|` để liệt kê phương án OR; so khớp chuẩn hóa Unicode NFC và không phân biệt hoa/thường
  (site có thể trả tiếng Việt dạng NFD).
- Test **không phụ thuộc thứ tự**: mỗi test tự mở trang cần thiết, không dựa vào trạng thái test trước
  (trừ việc dùng chung một cửa sổ Firefox trong cả phiên để chạy nhanh).

## 5. Kết quả và cách đánh giá
| Trạng thái | Ý nghĩa | Hành động |
|---|---|---|
| `PASS` | chạy được và khớp expected | – |
| `FAIL` | chạy được nhưng **kết quả khác expected** (có ảnh chụp) | xem `actual` + ảnh; có thể là lỗi site hoặc expected lỗi thời |
| `ERROR` | **lỗi hạ tầng/script**: timeout, không thấy phần tử, mất kết nối, driver | được thử lại theo `retries`; kiểm tra selector trong `app/pages/` |
| `SKIPPED` | `enabled=0` hoặc thiếu tài khoản | không tính vào tỉ lệ đạt |

`pass_rate = PASS / (tổng − SKIPPED)`. Tách FAIL và ERROR là có chủ đích: ERROR không phải bằng chứng site lỗi,
còn FAIL mới là phát hiện lỗi (hoặc cần cập nhật expected). Mật khẩu thật không bao giờ được ghi vào kết quả.

## 6. Chống flaky (kết quả chập chờn)
- Chỉ dùng **explicit wait** (implicit = 0); mỗi trang có điều kiện chờ riêng (đăng nhập: rời `/login` hoặc có lỗi
  server; tìm kiếm: có kết quả hoặc thông báo "không khớp").
- Banner cookie TrustArc được gỡ ở mỗi lần `open()` vì che nút bấm.
- `retries` chỉ áp dụng cho ERROR, không bao giờ cho FAIL (tránh "thử đến khi pass" che lỗi thật).
- Nghỉ `delay` giữa các test để tránh bị giới hạn tốc độ.
- **Dương tính giả đã biết:** tìm kiếm dùng Google CSE, chạy dày có thể hiện reCAPTCHA → `SR*` FAIL giả
  (xem `actual` có "xác nhận … rô-bốt"). Cách xử lý: tăng `delay`, chạy lại sau ít phút.

## 7. Quy trình khuyến nghị
1. **Smoke:** `python -m app.cli testcases/testcases.csv --delay 1` sau mỗi thay đổi code.
2. **Hồi quy đầy đủ:** chạy `khan_full.csv` từ GUI hoặc CLI (có tài khoản test để chạy cả `CR*`, `LG` đăng nhập đúng).
3. **CI:** CLI trả exit code 0/1; hoặc `pytest --junitxml=...` (xem [USAGE.md mục 2b](USAGE.md)).
4. Test FAIL: mở `report.html`, đối chiếu ảnh chụp và `actual`; nếu do site đổi giao diện thì sửa locator trong
   `app/pages/` hoặc `expected`, không nới lỏng đến mức test luôn pass.
5. Thêm test: sửa `tools/gen_testcases.py`, sinh lại, chạy riêng ID mới bằng `--ids`.

## 8. Hạn chế của phương pháp
- Phụ thuộc giao diện/văn bản của site thật → test có thể vỡ khi site cập nhật; không kiểm soát được dữ liệu.
- Không kiểm thử luồng ghi dữ liệu (đăng ký, đổi mật khẩu, làm bài), không kiểm thử tải, không kiểm thử truy cập (a11y).
- Chỉ một trình duyệt (Firefox) và một độ phân giải (1366x900); không chạy song song.
- Test âm tính đăng nhập dùng email giả; chúng chứng minh site *từ chối* dữ liệu sai, không chứng minh
  thông báo lỗi đúng với từng trường hợp (vì chỉ so khớp từ khóa chung).
