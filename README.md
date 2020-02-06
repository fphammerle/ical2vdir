# ical2vdir 📅

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI Pipeline Status](https://github.com/fphammerle/ical2vdir/workflows/tests/badge.svg)](https://github.com/fphammerle/ical2vdir/actions)
[![Coverage Status](https://coveralls.io/repos/github/fphammerle/ical2vdir/badge.svg?branch=master)](https://coveralls.io/github/fphammerle/ical2vdir?branch=master)
[![Last Release](https://img.shields.io/pypi/v/ical2vdir.svg)](https://pypi.org/project/ical2vdir/#history)
[![Compatible Python Versions](https://img.shields.io/pypi/pyversions/ical2vdir.svg)](https://pypi.org/project/ical2vdir/)

Convert / split single [iCalendar](https://en.wikipedia.org/wiki/ICalendar)
`.ics` file into a
[vdir](https://vdirsyncer.readthedocs.io/en/stable/vdir.html) directory.

Pre-existing files will be updated or left unchanged.

Compatible with [khal](https://github.com/pimutils/khal).

## Setup

```sh
$ sudo apt-get install python3-icalendar # optional
$ pip3 install --user --upgrade ical2vdir
```

## Usage

```sh
$ ical2vdir < input.ics --output-dir /some/path
```

Or download `.ics` from [Google Calendar](https://calendar.google.com/):
```sh
$ curl https://calendar.google.com/calendar/ical/someone%40gmail.com/private-1234/basic.ics \
    | pipenv run ical2vdir --output-dir output/
```

Remove files from output directory that are not available in input:
```sh
$ ical2vdir < input.ics --output-dir /some/path --delete
```
