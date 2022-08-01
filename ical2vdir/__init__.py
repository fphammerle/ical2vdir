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

import argparse
import datetime
import logging
import os
import shutil
import pathlib
import sys
import tempfile
import typing

import icalendar

_LOGGER = logging.getLogger(__name__)

_VDIR_EVENT_FILE_EXTENSION = ".ics"


def _event_prop_equal(prop_a: typing.Any, prop_b: typing.Any) -> bool:
    if isinstance(prop_a, list):
        return len(prop_a) == len(prop_b) and all(
            _event_prop_equal(*pair) for pair in zip(prop_a, prop_b)
        )
    if isinstance(prop_a, icalendar.prop.vDDDLists):
        # https://www.kanzaki.com/docs/ical/exdate.html
        return (
            isinstance(prop_b, icalendar.prop.vDDDLists)
            and len(prop_a.dts) == len(prop_b.dts)
            and all(_event_prop_equal(*pair) for pair in zip(prop_a.dts, prop_b.dts))
            and prop_a.params == prop_b.params
        )
    if isinstance(prop_a, (icalendar.prop.vDDDTypes, icalendar.prop.vCategory)):
        # pylint: disable=unidiomatic-typecheck
        return type(prop_a) == type(prop_b) and vars(prop_a) == vars(prop_b)
    return typing.cast(bool, prop_a == prop_b and prop_a.params == prop_b.params)


def _events_equal(event_a: icalendar.cal.Event, event_b: icalendar.cal.Event) -> bool:
    for key, prop_a in event_a.items():
        if key == "DTSTAMP":
            continue
        try:
            prop_b = event_b[key]
        except KeyError:
            _LOGGER.debug("%s: new key %s", event_a["UID"], key)
            return False
        if not _event_prop_equal(prop_a, prop_b):
            _LOGGER.debug(
                "%s/%s: %r != %r",
                event_a["UID"],
                key,
                prop_a,
                prop_b,
            )
            return False
    return True


def _datetime_basic_isoformat(dt_obj: datetime.datetime) -> str:
    # .isoformat() inserts unwanted separators
    return dt_obj.strftime("%Y%m%dT%H%M%S%z")


def _event_vdir_filename(event: icalendar.cal.Event) -> str:
    # > An item should contain a UID property as described by the vCard and iCalendar standards.
    # > [...] The filename should have similar properties as the UID of the file content.
    # > However, there is no requirement for these two to be the same.
    # > Programs may choose to store additional metadata in that filename, [...]
    # https://vdirsyncer.readthedocs.io/en/stable/vdir.html#basic-structure
    output_filename = str(event["UID"])
    if "RECURRENCE-ID" in event:
        recurrence_id = event["RECURRENCE-ID"]
        assert isinstance(recurrence_id.dt, datetime.datetime), recurrence_id.dt

        output_filename += "." + _datetime_basic_isoformat(recurrence_id.dt)
    return output_filename + _VDIR_EVENT_FILE_EXTENSION


def _write_event(event: icalendar.cal.Event, path: pathlib.Path) -> None:
    if path.is_dir():
        raise IsADirectoryError(path)  # similar to os.rename
    # > Creating and modifying items or metadata files should happen atomically.
    # https://vdirsyncer.readthedocs.io/en/stable/vdir.html#writing-to-vdirs
    temp_fd, temp_path = tempfile.mkstemp(
        prefix="ical2vdir-", suffix=_VDIR_EVENT_FILE_EXTENSION
    )
    try:
        # > Content lines are delimited by a line break,
        # > which is a CRLF sequence [...]
        # https://tools.ietf.org/html/rfc5545#section-3.1
        os.write(temp_fd, event.to_ical())
        os.close(temp_fd)
        shutil.move(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def _sync_event(
    event: icalendar.cal.Event, output_dir_path: pathlib.Path
) -> pathlib.Path:
    output_path = output_dir_path.joinpath(_event_vdir_filename(event))
    if not output_path.exists():
        _LOGGER.info("creating %s", output_path)
        _write_event(event, output_path)
    else:
        with output_path.open("rb") as current_file:
            current_event = icalendar.Event.from_ical(current_file.read())
        if _events_equal(event, current_event):
            _LOGGER.debug("%s is up to date", output_path)
        else:
            _LOGGER.info("updating %s", output_path)
            _write_event(event, output_path)
    return output_path


def _main() -> None:
    # https://docs.python.org/3/library/logging.html#levels
    logging.basicConfig(
        format="%(message)s",
        # datefmt='%Y-%m-%dT%H:%M:%S%z',
        level=logging.INFO,
    )
    argparser = argparse.ArgumentParser(
        description="Convert iCalendar .ics file to vdir directory."
        " Reads from stdin."
    )
    argparser.add_argument(
        "-o",
        "--output",
        "--output-dir",
        default=os.getcwd(),
        type=pathlib.Path,
        metavar="path",
        dest="output_dir_path",
        help="Path to output directory (default: current workings dir)",
    )
    argparser.add_argument(
        "--delete",
        action="store_true",
        help="Delete events not in input from output directory.",
    )
    argparser.add_argument(
        "-s",
        "--silent",
        "-q",
        "--quiet",
        action="store_true",
        help="Reduce verbosity.",
    )
    argparser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase verbosity",
    )
    args = argparser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(level=logging.DEBUG)
    elif args.silent:
        logging.getLogger().setLevel(level=logging.WARNING)
    calendar = icalendar.Calendar.from_ical(sys.stdin.read())
    _LOGGER.debug("%d subcomponents", len(calendar.subcomponents))
    extra_paths = set(
        path
        for path in args.output_dir_path.iterdir()
        if path.is_file() and path.name.endswith(_VDIR_EVENT_FILE_EXTENSION)
    )
    for component in calendar.subcomponents:
        if isinstance(component, icalendar.cal.Event):
            extra_paths.discard(
                _sync_event(event=component, output_dir_path=args.output_dir_path)
            )
        else:
            _LOGGER.debug("%s", component)
    _LOGGER.debug(
        "%d pre-existing items not in input: %s",
        len(extra_paths),
        ", ".join(p.name for p in extra_paths),
    )
    if args.delete:
        for path in extra_paths:
            _LOGGER.info("removing %s", path)
            path.unlink()
