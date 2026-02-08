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
import io
import logging
import pathlib
import subprocess
import unittest.mock

import _pytest.logging  # pylint: disable=import-private-name; tests
import icalendar

import ical2vdir

# pylint: disable=protected-access


def test_entrypoint_help() -> None:
    subprocess.run(["ical2vdir", "--help"], check=True, stdout=subprocess.PIPE)


def test__main_create_all(
    caplog: _pytest.logging.LogCaptureFixture,
    tmp_path: pathlib.Path,
    google_calendar_file: io.BufferedReader,
) -> None:
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch("sys.argv", ["", "--output-dir", str(tmp_path)]):
            with caplog.at_level(logging.INFO):
                ical2vdir._main()
    created_item_paths = sorted(tmp_path.iterdir())
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


def test__main_create_all_recurrence_id_date(
    caplog: _pytest.logging.LogCaptureFixture, tmp_path: pathlib.Path
) -> None:
    with pathlib.Path(__file__).parent.joinpath(
        "resources", "nextcloud-recurring.ics"
    ).open("rb") as calendar_file:
        with unittest.mock.patch("sys.stdin", calendar_file), unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(tmp_path)]
        ), caplog.at_level(logging.WARNING):
            ical2vdir._main()
    created_item_paths = sorted(tmp_path.iterdir())
    assert [p.name for p in created_item_paths] == [
        "b0fea373-389b-48d5-b739-9de3e298f555.20260101.ics",
        "b0fea373-389b-48d5-b739-9de3e298f555.20260201.ics",
        "b0fea373-389b-48d5-b739-9de3e298f555.20260301.ics",
    ]
    assert not caplog.records
    event = icalendar.cal.Event.from_ical(created_item_paths[1].read_bytes())
    assert isinstance(event, icalendar.cal.Event)
    assert event["UID"] == "b0fea373-389b-48d5-b739-9de3e298f555"
    assert event["SUMMARY"] == "second"
    assert event["RECURRENCE-ID"].dt == datetime.date(2026, 2, 1)


def test__main_create_all_tasks(
    caplog: _pytest.logging.LogCaptureFixture, tmp_path: pathlib.Path
) -> None:
    with pathlib.Path(__file__).parent.joinpath(
        "resources", "nextcloud-tasks.ics"
    ).open("rb") as calendar_file:
        with unittest.mock.patch("sys.stdin", calendar_file), unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(tmp_path)]
        ), caplog.at_level(logging.WARNING):
            ical2vdir._main()
    created_item_paths = sorted(tmp_path.iterdir())
    assert [p.name for p in created_item_paths] == [
        "1e6554b1-7ec6-4b58-9688-1dd141ea22cd.ics",
        "d6c1f8fa-0dfa-4d31-a988-6e7876fe3222.ics",
    ]
    assert not caplog.records
    task = icalendar.cal.Event.from_ical(created_item_paths[0].read_bytes())
    assert isinstance(task, icalendar.cal.Todo)
    assert task["UID"] == "1e6554b1-7ec6-4b58-9688-1dd141ea22cd"
    assert task["SUMMARY"] == "test 2"
    assert task["DUE"].dt == datetime.date(2026, 2, 9)


def test__main_create_some(
    caplog: _pytest.logging.LogCaptureFixture,
    tmp_path: pathlib.Path,
    google_calendar_file: io.BufferedReader,
) -> None:
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch("sys.argv", ["", "--output-dir", str(tmp_path)]):
            ical2vdir._main()
            tmp_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            google_calendar_file.seek(0)
            with caplog.at_level(logging.INFO):
                ical2vdir._main()
    assert len(caplog.records) == 1
    assert caplog.records[0].message.startswith("creating")
    assert caplog.records[0].message.endswith(
        "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
    )


def test__main_update(
    caplog: _pytest.logging.LogCaptureFixture,
    tmp_path: pathlib.Path,
    google_calendar_file: io.BufferedReader,
) -> None:
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch("sys.argv", ["", "--output-dir", str(tmp_path)]):
            ical2vdir._main()
            tmp_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            updated_path = tmp_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics"
            )
            updated_ical = updated_path.read_bytes().replace(b"20150908", b"20140703")
            with updated_path.open("wb") as updated_file:
                updated_file.write(updated_ical)
            google_calendar_file.seek(0)
            with caplog.at_level(logging.INFO):
                ical2vdir._main()
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
    caplog: _pytest.logging.LogCaptureFixture,
    tmp_path: pathlib.Path,
    google_calendar_file: io.BufferedReader,
) -> None:
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(tmp_path), "--silent"]
        ):
            ical2vdir._main()
            tmp_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            updated_path = tmp_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics"
            )
            updated_ical = updated_path.read_bytes().replace(b"20150908", b"20140703")
            with updated_path.open("wb") as updated_file:
                updated_file.write(updated_ical)
            google_calendar_file.seek(0)
            with caplog.at_level(logging.INFO):
                ical2vdir._main()
    assert len(caplog.records) == 0


def test__main_update_verbose(
    caplog: _pytest.logging.LogCaptureFixture,
    tmp_path: pathlib.Path,
    google_calendar_file: io.BufferedReader,
) -> None:
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(tmp_path), "--verbose"]
        ):
            ical2vdir._main()
            tmp_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150924T090000+0200.ics"
            ).unlink()
            updated_path = tmp_path.joinpath(
                "recurr1234567890qwertyuiop@google.com.20150908T090000+0200.ics"
            )
            updated_ical = updated_path.read_bytes().replace(b"20150908", b"20140703")
            with updated_path.open("wb") as updated_file:
                updated_file.write(updated_ical)
            google_calendar_file.seek(0)
            ical2vdir._main()
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
    caplog: _pytest.logging.LogCaptureFixture,
    tmp_path: pathlib.Path,
    google_calendar_file: io.BufferedReader,
) -> None:
    tmp_path.joinpath("will-be-deleted.ics").touch()
    with unittest.mock.patch("sys.stdin", google_calendar_file):
        with unittest.mock.patch(
            "sys.argv", ["", "--output-dir", str(tmp_path), "--delete"]
        ):
            with caplog.at_level(logging.INFO):
                ical2vdir._main()
    assert len(list(tmp_path.iterdir())) == 3
    assert not any(p.name == "will-be-deleted.ics" for p in tmp_path.iterdir())
    assert caplog.records[-1].message.startswith("removing")
    assert caplog.records[-1].message.endswith("will-be-deleted.ics")
