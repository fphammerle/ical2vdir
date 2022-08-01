# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2022-08-01
### Added
- `pyproject.toml` to specify build dependencies & build backend

### Removed
- compatibility with `python3.5` & `python3.6`

### Fixed
- fix export when output and temporary directory are on different filesystems
  (https://github.com/fphammerle/ical2vdir/pull/85)

## [0.1.2] - 2020-06-18
### Fixed
- python3.5:
  - `TypeError` in `_write_event` when renaming temporary file
  - `TypeError` in `_sync_event` when reading file
  - tests: `TypeError` when converting to `pathlib.Path`
  - tests: `AttributeError` due to unavailable `MagicMock.assert_called_once`

## [0.1.1] - 2020-02-06
### Fixed
- only write to disk when creating or updating item
- cleanup temporary files

## [0.1.0] - 2020-02-06

[Unreleased]: https://github.com/fphammerle/ical2vdir/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/fphammerle/ical2vdir/compare/v0.1.2...v1.0.0
[0.1.2]: https://github.com/fphammerle/ical2vdir/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/fphammerle/ical2vdir/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/fphammerle/ical2vdir/releases/tag/v0.1.0
