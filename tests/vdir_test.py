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

import copy
import os
import pathlib
import unittest.mock

import icalendar.cal
import pytest

import ical2vdir


def _normalize_ical(ical: bytes) -> bytes:
    return ical.replace(b"\n", b"\r\n")


_SINGLE_EVENT_ICAL = _normalize_ical(
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
"""
)

# pylint: disable=protected-access


def test__write_event_cleanup(tmpdir):
    event = icalendar.cal.Event.from_ical(_SINGLE_EVENT_ICAL)
    with unittest.mock.patch("os.unlink") as unlink_mock:
        with pytest.raises(IsADirectoryError):
            ical2vdir._write_event(event, pathlib.Path(tmpdir))
    unlink_mock.assert_called_once()
    unlink_args, _ = unlink_mock.call_args
    os.unlink(unlink_args[0])


@pytest.mark.parametrize(
    ("event_ical", "expected_filename"),
    [
        (_SINGLE_EVENT_ICAL, "1qa2ws3ed4rf5tg@google.com.ics",),
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
    assert ical2vdir._event_vdir_filename(event) == expected_filename


@pytest.mark.parametrize("event_ical", [_SINGLE_EVENT_ICAL])
def test__sync_event_create(tmpdir, event_ical):
    temp_path = pathlib.Path(tmpdir)
    event = icalendar.cal.Event.from_ical(event_ical)
    ical2vdir._sync_event(event, temp_path)
    (ics_path,) = temp_path.iterdir()
    assert ics_path.name == "1qa2ws3ed4rf5tg@google.com.ics"
    assert ics_path.read_bytes() == _SINGLE_EVENT_ICAL


@pytest.mark.parametrize("event_ical", [_SINGLE_EVENT_ICAL])
def test__sync_event_update(tmpdir, event_ical):
    temp_path = pathlib.Path(tmpdir)
    event = icalendar.cal.Event.from_ical(event_ical)
    ical2vdir._sync_event(event, temp_path)
    event["SUMMARY"] += " suffix"
    ical2vdir._sync_event(event, temp_path)
    (ics_path,) = temp_path.iterdir()
    assert ics_path.name == event["UID"] + ".ics"
    assert ics_path.read_bytes() == _SINGLE_EVENT_ICAL.replace(
        b"party", b"party suffix"
    )


@pytest.mark.parametrize("event_ical", [_SINGLE_EVENT_ICAL])
def test__sync_event_unchanged(tmpdir, event_ical):
    temp_path = pathlib.Path(tmpdir)
    event = icalendar.cal.Event.from_ical(event_ical)
    ical2vdir._sync_event(event, temp_path)
    (ics_path,) = temp_path.iterdir()
    old_stat = copy.deepcopy(ics_path.stat())
    ical2vdir._sync_event(event, temp_path)
    assert ics_path.stat() == old_stat
    assert ics_path.read_bytes() == _SINGLE_EVENT_ICAL
