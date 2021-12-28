# ical2vdir - convert .ics file to vdir directory
#
# Copyright (C) 2020 Fabian Peter Hammerle <fabian@hammerle.me>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime

import pytest

import ical2vdir

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
def test__datetime_basic_isoformat(
    dt_obj: datetime.datetime, expected_str: str
) -> None:
    # pylint: disable=protected-access
    assert ical2vdir._datetime_basic_isoformat(dt_obj) == expected_str
