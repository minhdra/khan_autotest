"""Kiểm thử module Tìm kiếm (Google CSE; có thể gặp captcha nếu chạy dày)."""
import pytest

from app.engine import Evaluator
from tests.conftest import cases_for

CASES = cases_for("Tìm kiếm")


@pytest.mark.parametrize("tc", CASES, ids=lambda t: t["id"])
def test_search(tc, khan):
    page = khan(tc)
    assert Evaluator.check(tc["expected_mode"], tc["expected"], page), (
        f"{tc['title']}: expected {tc['expected_mode']}={tc['expected']!r}; url={page.url}")
