# ics2vdir - convert .ics file to vdir directory
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
import logging
import os
import pathlib
import sys
import tempfile

import icalendar

_LOGGER = logging.getLogger(__name__)


def _event_prop_equal(prop_a, prop_b) -> bool:
    if isinstance(prop_a, icalendar.prop.vDDDLists):
        # https://www.kanzaki.com/docs/ical/exdate.html
        return (
            all(_event_prop_equal(*pair) for pair in zip(prop_a.dts, prop_b.dts))
            and len(prop_a.dts) == len(prop_b.dts)
            and prop_a.params == prop_b.params
        )
    if isinstance(prop_a, (icalendar.prop.vDDDTypes, icalendar.prop.vCategory)):
        # pylint: disable=unidiomatic-typecheck
        return type(prop_a) == type(prop_b) and vars(prop_a) == vars(prop_b)
    return prop_a == prop_b


def _events_equal(event_a: icalendar.cal.Event, event_b: icalendar.cal.Event) -> bool:
    for key, prop_a in event_a.items():
        if key == "DTSTAMP":
            continue
        prop_b = event_b[key]
        if not _event_prop_equal(prop_a, prop_b):
            _LOGGER.debug(
                "%s/%s: %r != %r", event_a["UID"], key, prop_a, prop_b,
            )
            return False
    return True


def _export_event(event: icalendar.cal.Event, output_dir_path: pathlib.Path) -> None:
    temp_fd, temp_path = tempfile.mkstemp(prefix="ics2vdir-", suffix=".ics")
    os.write(temp_fd, event.to_ical())
    os.close(temp_fd)
    output_path = output_dir_path.joinpath("{}.ics".format(event["UID"]))
    if not output_path.exists():
        _LOGGER.info("creating %s", output_path)
        os.rename(temp_path, output_path)
    else:
        with open(output_path, "rb") as current_file:
            current_event = icalendar.Event.from_ical(current_file.read())
        if _events_equal(event, current_event):
            _LOGGER.debug("%s is up to date", output_path)
        else:
            _LOGGER.info("updating %s", output_path)
            os.rename(temp_path, output_path)


def _main():
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
    args = argparser.parse_args()
    calendar = icalendar.Calendar.from_ical(sys.stdin.read())
    _LOGGER.debug("%d subcomponents", len(calendar.subcomponents))
    for component in calendar.subcomponents:
        if isinstance(component, icalendar.cal.Event):
            _export_event(event=component, output_dir_path=args.output_dir_path)
        else:
            _LOGGER.debug("%s", component)
