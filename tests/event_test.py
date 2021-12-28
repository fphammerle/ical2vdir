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

import icalendar.cal
import pytest

import ical2vdir


@pytest.mark.parametrize(
    ("event_a_ical", "event_b_ical", "expected_result"),
    (
        [
            (
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:123456789@google.com
SEQUENCE:0
CREATED:20191231T103841Z
DESCRIPTION:
LAST-MODIFIED:20191231T103841Z
LOCATION:
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
""",
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:123456789@google.com
SEQUENCE:0
CREATED:20191231T103841Z
DESCRIPTION:
LAST-MODIFIED:20191231T103841Z
LOCATION:
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
""",
                True,
            ),
            (
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:123456789@google.com
SEQUENCE:0
CREATED:20191231T103841Z
DESCRIPTION:
LAST-MODIFIED:20191231T103841Z
LOCATION:
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
""",
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:123456789@google.com
SEQUENCE:0
CREATED:20191231T103841Z
DESCRIPTION:
LAST-MODIFIED:20191231T103841Z
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
""",
                False,
            ),
            (
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:123456789@google.com
SEQUENCE:0
CREATED:20191231T103841Z
LAST-MODIFIED:20191231T103841Z
END:VEVENT
""",
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:123456789@google.com
SEQUENCE:1
CREATED:20191231T103841Z
LAST-MODIFIED:20191231T103841Z
END:VEVENT
""",
                False,
            ),
            (
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:123456789@google.com
SEQUENCE:0
CREATED:20191231T103841Z
LAST-MODIFIED:20191231T103841Z
END:VEVENT
""",
                # ignoring DTSTAMP
                """BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T200640Z
UID:123456789@google.com
SEQUENCE:0
CREATED:20191231T103841Z
LAST-MODIFIED:20191231T103841Z
END:VEVENT
""",
                True,
            ),
        ]
    ),
)
def test__events_equal(
    event_a_ical: str, event_b_ical: str, expected_result: bool
) -> None:
    event_a = icalendar.cal.Event.from_ical(event_a_ical)
    event_b = icalendar.cal.Event.from_ical(event_b_ical)
    # pylint: disable=protected-access
    assert ical2vdir._events_equal(event_a, event_b) == expected_result
