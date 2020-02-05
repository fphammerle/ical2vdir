import datetime
import typing

import pytest
from icalendar.prop import vCalAddress, vDDDLists, vDDDTypes, vInt, vRecur, vText

from ics2vdir import _event_prop_equal

_CEST = datetime.timezone(datetime.timedelta(hours=+2))


def _parametrize(obj: typing.Any, params: dict) -> typing.Any:
    for key, value in params.items():
        obj.params.__setitem__(key, value)
    return obj


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
        (vRecur(FREQ="WEEKLY", COUNT=21), vRecur(FREQ="WEEKLY", COUNT=21), True,),
        (vRecur(FREQ="WEEKLY", COUNT=21), vRecur(FREQ="WEEKLY", COUNT=42), False,),
        (
            vDDDTypes(
                datetime.datetime(2012, 7, 3, 16, 39, 2, tzinfo=datetime.timezone.utc)
            ),
            vDDDTypes(
                datetime.datetime(2012, 7, 3, 16, 39, 2, tzinfo=datetime.timezone.utc)
            ),
            True,
        ),
        (
            vDDDTypes(
                datetime.datetime(2012, 7, 3, 16, 39, 2, tzinfo=datetime.timezone.utc)
            ),
            vDDDTypes(datetime.datetime(2012, 7, 3, 18, 39, 2, tzinfo=_CEST)),
            # logically that should be True
            # but shouldn't hurt to update the ics file
            False,
        ),
        (
            vDDDTypes(
                datetime.datetime(2012, 7, 3, 16, 39, 3, tzinfo=datetime.timezone.utc)
            ),
            vDDDTypes(
                datetime.datetime(2012, 7, 3, 16, 39, 2, tzinfo=datetime.timezone.utc)
            ),
            False,
        ),
        (
            vDDDLists(
                [datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc)]
            ),
            vDDDLists(
                [datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc)]
            ),
            True,
        ),
        (
            vDDDLists(
                [
                    datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2020, 2, 5, 20, 5, tzinfo=datetime.timezone.utc),
                ]
            ),
            vDDDLists(
                [
                    datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2020, 2, 5, 20, 5, tzinfo=datetime.timezone.utc),
                ]
            ),
            True,
        ),
        (
            vDDDLists(
                [
                    datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2020, 2, 5, 20, 5, tzinfo=datetime.timezone.utc),
                ]
            ),
            vDDDLists(
                [
                    datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2020, 2, 5, 20, 7, tzinfo=datetime.timezone.utc),
                ]
            ),
            False,
        ),
        (
            vDDDLists(
                [
                    datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2020, 2, 5, 20, 5, tzinfo=datetime.timezone.utc),
                ]
            ),
            vDDDLists(
                [
                    datetime.datetime(2020, 2, 5, 20, 0, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2020, 2, 5, 20, 5, tzinfo=datetime.timezone.utc),
                    datetime.datetime(2020, 2, 5, 20, 7, tzinfo=datetime.timezone.utc),
                ]
            ),
            False,
        ),
        (
            vCalAddress("someelse@somewhere.com"),
            _parametrize(
                vCalAddress("someelse@somewhere.com"),
                dict(UTYPE="INDIVIDUAL", PARTSTAT="ACCEPTED"),
            ),
            False,
        ),
        (
            _parametrize(
                vCalAddress("someelse@somewhere.com"),
                dict(UTYPE="INDIVIDUAL", PARTSTAT="ACCEPTED"),
            ),
            _parametrize(
                vCalAddress("someelse@somewhere.com"),
                dict(UTYPE="INDIVIDUAL", PARTSTAT="ACCEPTED"),
            ),
            True,
        ),
        (
            [
                vCalAddress("someone@somewhere.com",),
                vCalAddress("someelse@somewhere.com"),
            ],
            [
                vCalAddress("someone@somewhere.com",),
                _parametrize(
                    vCalAddress("someelse@somewhere.com"),
                    dict(UTYPE="INDIVIDUAL", PARTSTAT="ACCEPTED"),
                ),
            ],
            False,
        ),
        (
            [
                vCalAddress("someone@somewhere.com",),
                _parametrize(
                    vCalAddress("someelse@somewhere.com"),
                    dict(UTYPE="INDIVIDUAL", PARTSTAT="ACCEPTED"),
                ),
            ],
            [
                vCalAddress("someone@somewhere.com",),
                _parametrize(
                    vCalAddress("someelse@somewhere.com"),
                    dict(UTYPE="INDIVIDUAL", PARTSTAT="ACCEPTED"),
                ),
            ],
            True,
        ),
    ],
)
def test__event_prop_equal(prop_a, prop_b, expected_result):
    assert _event_prop_equal(prop_a, prop_b) == expected_result
