import datetime

import pytest

import ics2vdir

_CEST = datetime.timezone(datetime.timedelta(hours=+2))


@pytest.mark.parametrize(
    ("dt_obj", "expected_str"),
    [
        (datetime.datetime(2012, 7, 17, 12, 0, tzinfo=_CEST), "20120717T120000+0200"),
        (
            datetime.datetime(2012, 7, 17, 12, 0, tzinfo=datetime.timezone.utc),
            "20120717T120000+0000",
        ),
    ],
)
def test__datetime_basic_isoformat(dt_obj, expected_str):
    # pylint: disable=protected-access
    assert ics2vdir._datetime_basic_isoformat(dt_obj) == expected_str
