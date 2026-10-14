"""Kiểm thử khóa học / tiến độ (một số test cần KHAN_EMAIL/KHAN_PASSWORD)."""
import pytest

from app.engine import Evaluator
from tests.conftest import cases_for

CASES = cases_for("Khóa học / Tiến độ")


@pytest.mark.parametrize("tc", CASES, ids=lambda t: t["id"])
def test_course(tc, khan):
    page = khan(tc)
    assert Evaluator.check(tc["expected_mode"], tc["expected"], page), (
        f"{tc['title']}: expected {tc['expected_mode']}={tc['expected']!r}; url={page.url}")
