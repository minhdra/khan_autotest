"""Tầng kiểm tra (assertion): so sánh kết quả thực tế với expected. Chỉ dùng API của page object."""
import unicodedata

from ..pages import SearchPage


def norm(s):
    """NFC + lower: trang web có thể trả tiếng Việt dạng tổ hợp (NFD)."""
    return unicodedata.normalize("NFC", s or "").lower()


class Evaluator:
    """So sánh kết quả thực tế với expected."""

    @staticmethod
    def check(mode, expected, page):
        """Chỉ dùng API của page object, không chạm driver/locator."""
        alts = [norm(e.strip()) for e in expected.split("|") if e.strip()] or [""]
        if mode == "url_contains":
            ok = any(a in norm(page.url) for a in alts)
        elif mode == "url_not_contains":
            ok = not any(a in norm(page.url) for a in alts)
        elif mode == "text_contains":
            t = norm(page.body_text())
            ok = any(a in t for a in alts)
        elif mode == "text_not_contains":
            t = norm(page.body_text())
            ok = not any(a in t for a in alts)
        elif mode == "title_contains":
            ok = any(a in norm(page.title) for a in alts)
        elif mode == "element_visible":
            ok = page.is_visible(expected)
        elif mode == "results_min":
            ok = SearchPage(page.d, page.base).result_count() >= int(expected or 1)
        else:
            raise ValueError(f"expected_mode không hợp lệ: {mode}")
        return ok
