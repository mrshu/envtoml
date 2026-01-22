# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning.

## [Unreleased]

## [0.4.0] - 2026-01-22
### Added
- Support for `${VAR:-default}` fallback syntax in env interpolation.
- Support for escaping literal dollar signs via `$$`.
- Support for multiple env vars inside a single string value.
- Support for env var replacement within list values.
- `fail_on_missing` option for strict missing-env handling.

### Changed
- Official support and CI testing now target Python 3.10+.

## [0.3.1] - 2026-01-17
### Added
- Support for multiple environment variables within a single string value.
- Documentation examples for multi-variable expansion.

## [0.3.0] - 2026-01-17
### Added
- `fail_on_missing` option for `load`/`loads` to raise on missing env vars.

### Changed
- Docs/tests updated for the new option and relaxed tomllib parity checks.

## [0.2.1] - 2026-01-17
### Changed
- Re-release to update PyPI artifacts for the 0.2.x line.

## [0.2.0] - 2026-01-17
### Added
- PEP 561 typing marker and typing-focused tests.
- GitHub Actions CI running pytest and ty.

### Changed
- Switched TOML parsing to stdlib tomllib (tomli fallback for Python < 3.11).
- Updated load/loads signatures to match tomllib.
- Adjusted tests and fixtures to valid TOML for tomllib.

### Removed
- Travis CI configuration.

## [0.1.3] - 2026-01-17
### Added
- uv lockfile and uv-based dev workflow.

### Changed
- Migrated project metadata to PEP 621 and switched the build backend to Hatchling.
- Updated test instructions to use uv.

### Removed
- Poetry lockfile.

## [0.1.2] - 2019-09-27
### Added
- Pytest-based test runner and coverage tooling.
- Travis CI and coverage configuration.

### Changed
- Python version constraints in project metadata.
- Package metadata naming tweaks.

### Fixed
- Removed a stray return in the processing logic.

### Docs
- README badges and copy updates.

## [0.1.1] - 2019-09-20
### Fixed
- README and metadata tweaks.

## [0.1.0] - 2019-09-20
### Added
- Initial release.
