import pytest
from icalendar.prop import vCalAddress, vInt, vText

from ics2vdir import _event_prop_equal


@pytest.mark.parametrize(
    ("prop_a", "prop_b", "expected_result"),
    [
        (vText("CONFIRMED"), vText("CONFIRMED"), True),
        (vText("TENTATIVE"), vText("TENTATIVE"), True),
        (vText("CONFIRMED"), vText("TENTATIVE"), False),
        (vText("CONFIRMED"), vInt(0), False),
        (vInt(0), vInt(0), True),
        (vInt(0), vInt(21), False),
        (
            vCalAddress("mailto:someone@somewhere.com"),
            vCalAddress("mailto:someone@somewhere.com"),
            True,
        ),
        (
            vCalAddress("mailto:someone@somewhere.com"),
            vCalAddress("mailto:someelse@somewhere.com"),
            False,
        ),
    ],
)
def test__event_prop_equal(prop_a, prop_b, expected_result):
    assert _event_prop_equal(prop_a, prop_b) == expected_result
