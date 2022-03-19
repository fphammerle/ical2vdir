import io
import pathlib
import typing

import pytest


@pytest.fixture
def google_calendar_file() -> typing.Iterator[io.BufferedReader]:
    with pathlib.Path(__file__).parent.joinpath(
        "resources", "google-calendar.ics"
    ).open("rb") as file:
        yield file
