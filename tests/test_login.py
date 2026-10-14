"""Kiểm thử module Đăng nhập (UI, hợp lệ, không hợp lệ, biên, Enter)."""
import pytest

from app.engine import Evaluator
from tests.conftest import cases_for

CASES = cases_for("Đăng nhập")


@pytest.mark.parametrize("tc", CASES, ids=lambda t: t["id"])
def test_login(tc, khan):
    page = khan(tc)
    assert Evaluator.check(tc["expected_mode"], tc["expected"], page), (
        f"{tc['title']}: expected {tc['expected_mode']}={tc['expected']!r}; url={page.url}")
