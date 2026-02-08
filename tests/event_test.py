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
            (
                """BEGIN:VEVENT
SUMMARY:exdate test unchanged
DTSTART;TZID=Europe/Vienna:20260120T160000
DTEND;TZID=Europe/Vienna:20260120T163000
DTSTAMP:20260130T123456Z
UID:c27cfee4-60a5-4bc4-9ab6-ef4fb3dce111
RRULE:FREQ=WEEKLY;WKST=TU
EXDATE;TZID=Europe/Vienna:20260120T160000
EXDATE;TZID=Europe/Vienna:20260127T160000
END:VEVENT
""",
                """BEGIN:VEVENT
SUMMARY:exdate test unchanged
DTSTART;TZID=Europe/Vienna:20260120T160000
DTEND;TZID=Europe/Vienna:20260120T163000
DTSTAMP:20260130T123457Z
UID:c27cfee4-60a5-4bc4-9ab6-ef4fb3dce111
RRULE:FREQ=WEEKLY;WKST=TU
EXDATE;TZID=Europe/Vienna:20260120T160000
EXDATE;TZID=Europe/Vienna:20260127T160000
END:VEVENT
""",
                True,
            ),
            (
                """BEGIN:VEVENT
SUMMARY:exdate test changed
DTSTART;TZID=Europe/Vienna:20260120T160000
DTEND;TZID=Europe/Vienna:20260120T163000
DTSTAMP:20260130T123456Z
UID:c27cfee4-60a5-4bc4-9ab6-ef4fb3dce111
RRULE:FREQ=WEEKLY;WKST=TU
EXDATE;TZID=Europe/Vienna:20260120T160000
EXDATE;TZID=Europe/Vienna:20260127T160000
END:VEVENT
""",
                """BEGIN:VEVENT
SUMMARY:exdate test changed
DTSTART;TZID=Europe/Vienna:20260120T160000
DTEND;TZID=Europe/Vienna:20260120T163000
DTSTAMP:20260130T123456Z
UID:c27cfee4-60a5-4bc4-9ab6-ef4fb3dce111
RRULE:FREQ=WEEKLY;WKST=TU
EXDATE;TZID=Europe/Vienna:20260120T160000
END:VEVENT
""",
                False,
            ),
            (
                b"""BEGIN:VEVENT
UID:d6c1f8fa-0dfa-4d31-a988-6e7876fe3222
DTSTAMP:20260208T070338Z
SUMMARY:test
DTSTART;VALUE=DATE:20260208
END:VEVENT
""",
                b"""BEGIN:VTODO
UID:d6c1f8fa-0dfa-4d31-a988-6e7876fe3222
DTSTAMP:20260208T070338Z
SUMMARY:test
DTSTART;VALUE=DATE:20260208
END:VTODO
""",
                False,
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
