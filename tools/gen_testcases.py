"""Sinh bộ test case đầy đủ -> testcases/khan_full.csv + khan_full.xlsx (có định dạng đẹp)."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "testcases"
COLS = ["id", "module", "title", "type", "priority", "scenario", "input1", "input2",
        "expected_mode", "expected", "note", "enabled"]
rows = []


def add(prefix, module, title, typ, pri, scen, i1="", i2="", mode="", exp="", note="", enabled=1):
    n = sum(1 for r in rows if r[0].startswith(prefix)) + 1
    rows.append([f"{prefix}{n:02d}", module, title, typ, pri, scen, i1, i2, mode, exp, note, enabled])


GOODPW, GOODMAIL = "Abcd@1234", "autotest.user.9271@example.com"
STAY = ("url_contains", "/login")
ERRTXT = ("text_contains", "không đúng|incorrect|không hợp lệ|invalid")

# ---------------- Đăng nhập: giao diện ----------------
M = "Đăng nhập"
add("LG", M, "Hiển thị ô email/tên đăng nhập", "UI", "High", "open_page", "/login", "", "element_visible", "#username-field")
add("LG", M, "Hiển thị ô mật khẩu (ẩn ký tự)", "UI", "High", "open_page", "/login", "", "element_visible", "input[type=password]")
add("LG", M, "Hiển thị nút Đăng nhập", "UI", "High", "open_page", "/login", "", "element_visible", "[data-testid=log-in-submit-button]")
add("LG", M, "Có nút đăng nhập bằng Google", "UI", "Low", "open_page", "/login", "", "text_contains", "Tiếp tục bằng Google")
add("LG", M, "Có liên kết Quên mật khẩu", "UI", "Low", "open_page", "/login", "", "text_contains", "Quên mật khẩu")
add("LG", M, "Có liên kết Đăng ký tài khoản", "UI", "Low", "open_page", "/login", "", "text_contains", "Đăng ký")
add("LG", M, "Tiêu đề tab chứa Khan Academy", "UI", "Low", "open_page", "/login", "", "title_contains", "Khan Academy")
# ---------------- Đăng nhập: âm tính / biên ----------------
add("LG", M, "Email không tồn tại, mật khẩu hợp lệ (8 ký tự)", "Negative", "High", "login", GOODMAIL, GOODPW, *ERRTXT, "Báo lỗi sai thông tin")
add("LG", M, "Email không tồn tại, mật khẩu 12 ký tự", "Boundary", "Medium", "login", GOODMAIL, "Abcd@1234567", *ERRTXT, "Biên trên độ dài mật khẩu")
add("LG", M, "Để trống cả email và mật khẩu", "Negative", "High", "login", "", "", *STAY, "Ở lại trang login")
add("LG", M, "Để trống mật khẩu", "Negative", "High", "login", GOODMAIL, "", *STAY)
add("LG", M, "Để trống email", "Negative", "High", "login", "", GOODPW, *STAY)
add("LG", M, "Email thiếu ký tự @", "Negative", "Medium", "login", "autotest.user.9271example.com", GOODPW, *STAY)
add("LG", M, "Email thiếu phần tên miền (@gmail.com)", "Negative", "Medium", "login", "autotest.user.9271", GOODPW, *STAY)
add("LG", M, "Email có dấu cách trước @", "Negative", "Medium", "login", "autotest.user.9271 @example.com", GOODPW, *STAY)
add("LG", M, "Email có dấu cách sau @", "Negative", "Medium", "login", "autotest.user.9271@ example.com", GOODPW, *STAY)
add("LG", M, "Email viết hoa toàn bộ (không tồn tại)", "Equivalence", "Low", "login", GOODMAIL.upper(), GOODPW, *ERRTXT)
add("LG", M, "Tên đăng nhập không có @", "Equivalence", "Low", "login", "autotest_user_9271", GOODPW, *ERRTXT)
add("LG", M, "Mật khẩu 7 ký tự (dưới biên 8)", "Boundary", "Medium", "login", GOODMAIL, "Ab@1234", *STAY)
add("LG", M, "Mật khẩu 13 ký tự (trên biên 12)", "Boundary", "Medium", "login", GOODMAIL, "Abcd@12345678", *ERRTXT)
add("LG", M, "Mật khẩu chỉ gồm chữ cái", "Equivalence", "Low", "login", GOODMAIL, "abcdefgh", *ERRTXT)
add("LG", M, "Mật khẩu chỉ gồm số", "Equivalence", "Low", "login", GOODMAIL, "12345678", *ERRTXT)
add("LG", M, "Mật khẩu chỉ gồm ký tự đặc biệt", "Equivalence", "Low", "login", GOODMAIL, "!@#$%^&*", *ERRTXT)
add("LG", M, "Mật khẩu chứa dấu cách", "Negative", "Low", "login", GOODMAIL, "Abcd 1234", *ERRTXT)
add("LG", M, "Email rất dài (250 ký tự)", "Boundary", "Low", "login", "a" * 240 + "@example.com", GOODPW, *STAY)
add("LG", M, "Gửi form bằng phím Enter (sai thông tin)", "Functional", "Medium", "login_enter", GOODMAIL, GOODPW, *ERRTXT, "Enter hoạt động như nút")
add("LG", M, "Chuỗi SQL Injection ở ô email", "Security", "High", "login", "' OR '1'='1", GOODPW, *STAY, "Không được đăng nhập")
add("LG", M, "Chuỗi SQL Injection ở ô mật khẩu", "Security", "High", "login", GOODMAIL, "' OR '1'='1' --", *STAY, "Không được đăng nhập")
add("LG", M, "Chuỗi XSS ở ô email không bị thực thi", "Security", "High", "login", "<script>alert(1)</script>", GOODPW, *STAY)
add("LG", M, "Đăng nhập đúng tài khoản hợp lệ", "Functional", "High", "login", "{EMAIL}", "{PASSWORD}", "url_not_contains", "/login", "Cần tài khoản thật")
add("LG", M, "Sau đăng nhập đúng, không lộ mật khẩu trên URL", "Security", "High", "login", "{EMAIL}", "{PASSWORD}", "url_not_contains", "password", "Cần tài khoản thật")

# ---------------- Tìm kiếm ----------------
M = "Tìm kiếm"
add("SR", M, "Có ô tìm kiếm trên trang tìm kiếm", "UI", "High", "open_page", "/search", "", "element_visible", "[data-testid=page-search-box]")
add("SR", M, "Từ khóa tiếng Anh hợp lệ: algebra", "Functional", "High", "search", "algebra", "", "results_min", "1")
add("SR", M, "Từ khóa tiếng Việt có dấu: toán", "Functional", "High", "search", "toán", "", "results_min", "1")
add("SR", M, "Từ khóa tiếng Việt: hình học", "Functional", "Medium", "search", "hình học", "", "results_min", "1")
add("SR", M, "Từ khóa không dấu: toan", "Equivalence", "Medium", "search", "toan", "", "results_min", "1")
add("SR", M, "Từ khóa viết hoa: ALGEBRA", "Equivalence", "Medium", "search", "ALGEBRA", "", "results_min", "1")
add("SR", M, "Từ khóa nhiều từ: linear equations", "Functional", "Medium", "search", "linear equations", "", "results_min", "1")
add("SR", M, "Từ khóa theo môn: biology", "Functional", "Medium", "search", "biology", "", "results_min", "1")
add("SR", M, "Từ khóa theo kiểu nội dung: video", "Functional", "Low", "search", "video", "", "results_min", "1")
add("SR", M, "Từ khóa 1 chữ cái", "Boundary", "Medium", "search", "a", "", "text_contains", "Tất cả kết quả")
add("SR", M, "Từ khóa là số: 2024", "Equivalence", "Medium", "search", "2024", "", "text_contains", "Tất cả kết quả")
add("SR", M, "Từ khóa số 0", "Boundary", "Low", "search", "0", "", "text_contains", "Tất cả kết quả")
add("SR", M, "Từ khóa số âm: -1", "Boundary", "Low", "search", "-1", "", "text_contains", "Tất cả kết quả")
add("SR", M, "Từ khóa ký tự đặc biệt: @#$%", "Equivalence", "Medium", "search", "@#$%", "", "text_contains", "Tất cả kết quả")
add("SR", M, "Từ khóa có dấu nháy kép", "Equivalence", "Low", "search", '"algebra"', "", "text_contains", "Tất cả kết quả")
add("SR", M, "Từ khóa có emoji", "Equivalence", "Low", "search", "📚", "", "text_contains", "Tất cả kết quả")
add("SR", M, "Từ khóa không tồn tại", "Negative", "High", "search", "zzqqxxwwvv9", "", "text_contains", "không khớp|did not match", "Báo không có kết quả")
add("SR", M, "Từ khóa dài 100 ký tự", "Boundary", "Low", "search", "a" * 100, "", "text_contains", "không khớp|did not match|Tất cả kết quả")
add("SR", M, "Từ khóa dài 200 ký tự", "Boundary", "Low", "search", "a" * 200, "", "text_contains", "không khớp|did not match|Tất cả kết quả")
add("SR", M, "Từ khóa có dấu cách đầu/cuối", "Equivalence", "Low", "search", "  algebra  ", "", "results_min", "1")
add("SR", M, "Từ khóa chỉ gồm dấu cách", "Negative", "Low", "search", "     ", "", "url_contains", "/search")
add("SR", M, "Không nhập từ khóa", "Negative", "Medium", "search", "", "", "url_contains", "/search")
add("SR", M, "Chuỗi SQL Injection bị chặn, không lộ lỗi CSDL", "Security", "High", "search", "' OR 1=1 --", "", "text_not_contains", "SQL syntax|Traceback|Internal Server Error|stack trace", "Site trả HTTP 406 (WAF), trang rỗng")
add("SR", M, "Chuỗi XSS bị chặn, không phản chiếu ra trang", "Security", "High", "search", "<script>alert(1)</script>", "", "text_not_contains", "<script>alert|Traceback|Internal Server Error", "Site trả HTTP 406 (WAF), trang rỗng")

# ---------------- Điều hướng ----------------
M = "Điều hướng"
add("NV", M, "Trang chủ tải được", "Functional", "High", "open_page", "/", "", "title_contains", "Khan Academy")
add("NV", M, "Trang chủ có nút Đăng nhập", "UI", "High", "open_page", "/", "", "element_visible", "a[href*='/login']")
add("NV", M, "Bấm Đăng nhập ở header chuyển sang /login", "Functional", "High", "click", "/", "a[href*='/login']", "url_contains", "/login")
add("NV", M, "Có nút Khám phá (menu môn học)", "UI", "Medium", "open_page", "/", "", "element_visible", "[data-testid=learn-menu-dropdown]")
add("NV", M, "Có nút Tìm kiếm trên header", "UI", "Medium", "open_page", "/", "", "element_visible", "[data-testid=navbar-search-button]")
add("NV", M, "Bấm nút Tìm kiếm mở trang/ô tìm kiếm", "Functional", "Medium", "click", "/", "[data-testid=navbar-search-button]", "element_visible", "[data-testid=page-search-box], input[type=search]")
add("NV", M, "Có liên kết Quyên góp", "UI", "Low", "open_page", "/", "", "element_visible", "[data-testid=header-donate-link]")
add("NV", M, "Trang Toán học", "Functional", "Medium", "open_page", "/math", "", "url_contains", "/math")
add("NV", M, "Trang Khoa học", "Functional", "Medium", "open_page", "/science", "", "url_contains", "/science")
add("NV", M, "Trang Máy tính/Lập trình", "Functional", "Medium", "open_page", "/computing", "", "url_contains", "/computing")
add("NV", M, "Trang Kinh tế - Tài chính", "Functional", "Low", "open_page", "/economics-finance-domain", "", "url_contains", "/economics-finance-domain")
add("NV", M, "Trang Luyện thi", "Functional", "Low", "open_page", "/test-prep", "", "url_contains", "/test-prep")
add("NV", M, "Trang Giới thiệu (About)", "Functional", "Low", "open_page", "/about/our-mission", "", "text_contains", "Khan Academy")
add("NV", M, "Trang đăng ký tải được", "Functional", "Medium", "open_page", "/signup", "", "url_contains", "/signup|/login")
add("NV", M, "Trang quên mật khẩu tải được", "Functional", "Low", "open_page", "/forgot-password", "", "url_contains", "/forgot|/login")
add("NV", M, "URL không tồn tại hiển thị trang 404", "Negative", "Medium", "open_page", "/trang-khong-ton-tai-autotest", "", "text_contains", "không tồn tại|not found|404")
add("NV", M, "Trang 404 có liên kết về trang chủ", "Negative", "Low", "open_page", "/trang-khong-ton-tai-autotest", "", "text_contains", "trang chủ|home")

# ---------------- Khóa học & tiến độ (cần tài khoản, chỉ đọc) ----------------
M = "Khóa học / Tiến độ"
add("CR", M, "Mở trang Khóa học của tôi", "Functional", "High", "login_then_open", "/profile/me/courses", "", "url_contains", "/profile/me/courses", "Cần tài khoản; chỉ đọc")
add("CR", M, "Trang Khóa học có nút chỉnh sửa", "UI", "Medium", "login_then_open", "/profile/me/courses", "", "text_contains", "Edit courses|Chỉnh sửa khóa học|Chỉnh sửa", "Cần tài khoản; chỉ đọc")
add("CR", M, "Mở trang Tiến độ học tập", "Functional", "High", "login_then_open", "/profile/me/progress", "", "url_contains", "/profile/me/progress", "Cần tài khoản; chỉ đọc")
add("CR", M, "Mở trang Hồ sơ cá nhân", "Functional", "Medium", "login_then_open", "/profile/me", "", "url_contains", "/profile/", "Cần tài khoản; chỉ đọc")
add("CR", M, "Mở trang Cài đặt tài khoản", "Functional", "Medium", "login_then_open", "/settings", "", "url_contains", "/settings", "Cần tài khoản; chỉ đọc")
add("CR", M, "Trang chủ sau đăng nhập không còn nút Đăng nhập", "Functional", "Medium", "login_then_open", "/", "", "text_not_contains", "Quên mật khẩu", "Cần tài khoản; chỉ đọc")

# ---------------- Bảo mật / kỹ thuật cơ bản ----------------
M = "Bảo mật & kỹ thuật"
add("SC", M, "HTTP tự chuyển sang HTTPS", "Security", "High", "open_page", "http://vi.khanacademy.org/login", "", "url_contains", "https://")
add("SC", M, "Ô mật khẩu có type=password", "Security", "High", "open_page", "/login", "", "element_visible", "input[type=password]")
add("SC", M, "Trang đăng nhập dùng HTTPS", "Security", "High", "open_page", "/login", "", "url_contains", "https://")
add("SC", M, "Có tệp robots.txt", "Functional", "Low", "open_page", "/robots.txt", "", "text_contains", "User-agent")
add("SC", M, "Sai thông tin không đưa mật khẩu lên URL", "Security", "High", "login", GOODMAIL, GOODPW, "url_not_contains", "Abcd")

with open(OUT / "khan_full.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(COLS)
    w.writerows(rows)

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

wb = Workbook()
ws = wb.active
ws.title = "TestCases"
ws.append(COLS)
thin = Side(style="thin", color="D5DBE1")
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor="0F4C45")
    c.alignment = Alignment(vertical="center")
for r in rows:
    ws.append(r)
widths = [8, 20, 48, 12, 9, 17, 34, 16, 18, 34, 26, 8]
for i, w_ in enumerate(widths):
    ws.column_dimensions[chr(65 + i)].width = w_
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = Border(bottom=thin)
pri = {"High": "FADBD8", "Medium": "FCF3CF", "Low": "D5F5E3"}
for k, v in pri.items():
    ws.conditional_formatting.add(f"E2:E{ws.max_row}", FormulaRule(formula=[f'$E2="{k}"'], fill=PatternFill("solid", bgColor=v)))
ws.freeze_panes = "D2"
ws.auto_filter.ref = ws.dimensions
dv = DataValidation(type="list", formula1='"login,login_enter,login_then_open,search,open_page,click"')
ws.add_data_validation(dv); dv.add(f"F2:F{ws.max_row+200}")
dv2 = DataValidation(type="list", formula1='"url_contains,url_not_contains,text_contains,text_not_contains,title_contains,element_visible,results_min"')
ws.add_data_validation(dv2); dv2.add(f"I2:I{ws.max_row+200}")
dv3 = DataValidation(type="list", formula1='"High,Medium,Low"')
ws.add_data_validation(dv3); dv3.add(f"E2:E{ws.max_row+200}")

g = wb.create_sheet("Hướng dẫn")
for line in [
    ("Cột", "Ý nghĩa"),
    ("id", "Mã test case (duy nhất)"), ("module", "Nhóm chức năng"), ("title", "Mô tả ngắn"),
    ("type", "Loại: UI / Functional / Negative / Boundary / Equivalence / Security"),
    ("priority", "High / Medium / Low"),
    ("scenario", "login, login_enter, login_then_open, search, open_page, click"),
    ("input1 / input2", "Dữ liệu vào, tùy kịch bản (email/mật khẩu, từ khóa, đường dẫn, CSS selector)"),
    ("expected_mode", "url_contains, url_not_contains, text_contains, text_not_contains, title_contains, element_visible, results_min (dùng | để OR)"),
    ("expected", "Giá trị mong đợi"), ("enabled", "1 = chạy, 0 = bỏ qua"),
    ("{EMAIL} / {PASSWORD}", "Được thay bằng tài khoản nhập ở giao diện, không lưu vào file"),
]:
    g.append(line)
g["A1"].font = g["B1"].font = Font(bold=True)
g.column_dimensions["A"].width = 24; g.column_dimensions["B"].width = 110
wb.save(OUT / "khan_full.xlsx")
print(len(rows), "test case ->", OUT)
