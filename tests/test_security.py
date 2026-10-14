"""Kiểm thử bảo mật & kỹ thuật (HTTPS, tiêu đề, v.v.)."""
import pytest

from app.engine import Evaluator
from tests.conftest import cases_for

CASES = cases_for("Bảo mật & kỹ thuật")


@pytest.mark.parametrize("tc", CASES, ids=lambda t: t["id"])
def test_security(tc, khan):
    page = khan(tc)
    assert Evaluator.check(tc["expected_mode"], tc["expected"], page), (
        f"{tc['title']}: expected {tc['expected_mode']}={tc['expected']!r}; url={page.url}")
