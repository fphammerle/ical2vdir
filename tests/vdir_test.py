import icalendar.cal
import pytest

import ics2vdir


@pytest.mark.parametrize(
    ("event_ical", "expected_filename"),
    [
        (
            b"""BEGIN:VEVENT
SUMMARY:party
DTSTART:20201024T100000Z
DTEND:20201026T120000Z
DTSTAMP:20200205T160640Z
UID:1qa2ws3ed4rf5tg@google.com
SEQUENCE:0
CREATED:20191231T103841Z
DESCRIPTION:
LAST-MODIFIED:20191231T103841Z
LOCATION:
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
""",
            "1qa2ws3ed4rf5tg@google.com.ics",
        ),
        (
            b"""BEGIN:VEVENT
SUMMARY:work
DTSTART;TZID=Europe/Vienna:20150924T090000
DTEND;TZID=Europe/Vienna:20150924T123000
DTSTAMP:20200205T160640Z
UID:1qa2ws3ed4rf5tg@google.com
RECURRENCE-ID;TZID=Europe/Vienna:20150924T090000
SEQUENCE:5
CREATED:20140228T212925Z
DESCRIPTION:
LAST-MODIFIED:20150908T181423Z
LOCATION:
STATUS:CONFIRMED
TRANSP:TRANSPARENT
END:VEVENT
""",
            "1qa2ws3ed4rf5tg@google.com.20150924T090000+0200.ics",
        ),
    ],
)
def test__event_vdir_filename(event_ical, expected_filename):
    event = icalendar.cal.Event.from_ical(event_ical)
    # pylint: disable=protected-access
    assert ics2vdir._event_vdir_filename(event) == expected_filename
