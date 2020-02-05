# ics2vdir

Convert / split single [iCalendar](https://en.wikipedia.org/wiki/ICalendar)
`.ics` file into a
[vdir](https://vdirsyncer.readthedocs.io/en/stable/vdir.html) directory.

Compatible with [khal](https://github.com/pimutils/khal).

## Setup

```sh
$ sudo apt-get install python3-icalendar # optional
$ pip3 install --user --upgrade ics2vdir
```

## Usage

```sh
$ ics2vdir < input.ics --output-dir /some/path
```

Or download `.ics` from [Google Calendar](https://calendar.google.com/):
```sh
$ curl https://calendar.google.com/calendar/ical/someone%40gmail.com/private-1234/basic.ics \
    | pipenv run ics2vdir --output-dir output/
```

Remove files from output directory that are not available in input:
```sh
$ ics2vdir < input.ics --output-dir /some/path --delete
```

### Run Tests

```sh
$ git clone https://github.com/fphammerle/ics2vdir.git
$ cd ics2vdir
$ pipenv sync --dev
$ pipenv run pylint ics2vdir
```
