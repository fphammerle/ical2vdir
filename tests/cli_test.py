import io
import logging
import pathlib
import subprocess
import unittest.mock

import icalendar

import ics2vdir

# pylint: disable=protected-access


def test_entrypoint_help():
    subprocess.run(["ics2vdir", "--help"], check=True, stdout=subprocess.PIPE)


def test__main_create_all(
    caplog, temp_dir_path: pathlib.Path, google_calendar_file: io.BufferedReader
):
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch("sys.argv", ["", "--output-dir", str(temp_dir_path)]):
            with caplog.at_level(logging.INFO):
                ics2vdir._main()
    created_item_paths = sorted(temp_dir_path.iterdir())
    assert [p.name for p in created_item_paths] == [
        "1234567890qwertyuiopasdfgh@google.com.ics",
        "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics",
        "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics",
    ]
    assert len(caplog.records) == len(created_item_paths)
    for item_path in created_item_paths:
        assert any(
            item_path.name in record.message and "creating" in record.message
            for record in caplog.records
        )
    event = icalendar.cal.Event.from_ical(created_item_paths[1].read_bytes())
    assert isinstance(event, icalendar.cal.Event)
    assert event["UID"] == "recurr1234567890qwertyuiop@google.com"
    assert event["SUMMARY"] == "recurring"


def test__main_create_some(
    caplog, temp_dir_path: pathlib.Path, google_calendar_file: io.BufferedReader
):
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch("sys.argv", ["", "--output-dir", str(temp_dir_path)]):
            ics2vdir._main()
            temp_dir_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            google_calendar_file.seek(0)
            with caplog.at_level(logging.INFO):
                ics2vdir._main()
    assert len(caplog.records) == 1
    assert caplog.records[0].message.startswith("creating")
    assert caplog.records[0].message.endswith(
        "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
    )


def test__main_update(
    caplog, temp_dir_path: pathlib.Path, google_calendar_file: io.BufferedReader
):
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch("sys.argv", ["", "--output-dir", str(temp_dir_path)]):
            ics2vdir._main()
            temp_dir_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            updated_path = temp_dir_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics"
            )
            updated_ical = updated_path.read_bytes().replace(b"20150908", b"20140703")
            with updated_path.open("wb") as updated_file:
                updated_file.write(updated_ical)
            google_calendar_file.seek(0)
            with caplog.at_level(logging.INFO):
                ics2vdir._main()
    assert len(caplog.records) == 2
    log_records = sorted(caplog.records, key=lambda r: r.message)
    assert log_records[0].message.startswith("creating")
    assert log_records[0].message.endswith(
        "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
    )
    assert log_records[1].message.startswith("updating")
    assert log_records[1].message.endswith(
        "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics"
    )


def test__main_update_silent(
    caplog, temp_dir_path: pathlib.Path, google_calendar_file: io.BufferedReader
):
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(temp_dir_path), "--silent"]
        ):
            ics2vdir._main()
            temp_dir_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            updated_path = temp_dir_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics"
            )
            updated_ical = updated_path.read_bytes().replace(b"20150908", b"20140703")
            with updated_path.open("wb") as updated_file:
                updated_file.write(updated_ical)
            google_calendar_file.seek(0)
            with caplog.at_level(logging.INFO):
                ics2vdir._main()
    assert len(caplog.records) == 0


def test__main_update_verbose(
    caplog, temp_dir_path: pathlib.Path, google_calendar_file: io.BufferedReader
):
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(temp_dir_path), "--verbose"]
        ):
            ics2vdir._main()
            temp_dir_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            updated_path = temp_dir_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics"
            )
            updated_ical = updated_path.read_bytes().replace(b"20150908", b"20140703")
            with updated_path.open("wb") as updated_file:
                updated_file.write(updated_ical)
            google_calendar_file.seek(0)
            ics2vdir._main()
    assert any(
        r.message.endswith("1234567890qwertyuiopasdfgh@google.com.ics is up to date")
        for r in caplog.records
    )
    assert any(
        r.message.startswith("creating")
        and r.message.endswith(".20150924T090000+0200.ics")
        for r in caplog.records
    )
    assert any(
        r.message.startswith("updating")
        and r.message.endswith(".20150908T090000+0200.ics")
        for r in caplog.records
    )


def test__main_delete(
    caplog, temp_dir_path: pathlib.Path, google_calendar_file: io.BufferedReader
):
    temp_dir_path.joinpath("will-be-deleted.ics").touch()
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(temp_dir_path), "--delete"]
        ):
            with caplog.at_level(logging.INFO):
                ics2vdir._main()
    assert len(list(temp_dir_path.iterdir())) == 3
    assert not any(p.name == "will-be-deleted.ics" for p in temp_dir_path.iterdir())
    assert caplog.records[-1].message.startswith("removing")
    assert caplog.records[-1].message.endswith("will-be-deleted.ics")
