import io
import pathlib
import typing

import pytest


@pytest.fixture
def temp_dir_path(tmpdir) -> pathlib.Path:
    return pathlib.Path(tmpdir)


@pytest.fixture
def google_calendar_file() -> typing.Iterator[io.BufferedReader]:
    with pathlib.Path(__file__).parent.joinpath(
        "resources", "google-calendar.ics"
    ).open("rb") as file:
        yield typing.cast(io.BufferedReader, file)
