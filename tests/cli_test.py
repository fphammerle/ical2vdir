import io
import pathlib
import subprocess
import unittest.mock

import icalendar

import ics2vdir

# pylint: disable=protected-access


def test_entrypoint_help():
    subprocess.run(["ics2vdir", "--help"], check=True, stdout=subprocess.PIPE)


def test__main_create(
    temp_dir_path: pathlib.Path, google_calendar_file: io.BufferedReader
):
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch("sys.argv", ["", "--output-dir", str(temp_dir_path)]):
            ics2vdir._main()
    created_item_paths = sorted(temp_dir_path.iterdir())
    assert [p.name for p in created_item_paths] == [
        "1234567890qwertyuiopasdfgh@google.com.ics",
        "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics",
        "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics",
    ]
    event = icalendar.cal.Event.from_ical(created_item_paths[1].read_bytes())
    assert isinstance(event, icalendar.cal.Event)
    assert event["UID"] == "recurr1234567890qwertyuiop@google.com"
    assert event["SUMMARY"] == "recurring"
