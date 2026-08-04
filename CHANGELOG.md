# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-04

### Changed

- **BREAKING:** Sentry is now initialised with `include_local_variables=False` by
  default, so local variables are no longer attached to stack frames sent to
  Sentry. If you rely on local variables in Sentry events, set
  `'OPTIONS': {'include_local_variables': True}` in your `SENTRY` config.

## [0.2.0] - 2026-07-27

### Changed

- **BREAKING:** Celery support now requires the `celery` extra. If you use the
  Celery integration (`opinionated_structlog_config.celery`), install
  `opinionated-structlog-config[celery]` — `celery.py` imports `celery` and
  `django_structlog.celery` at module level, and those are no longer pulled in
  by the base install.

### Added

- `celery` extra that installs `celery` and `django-structlog`.
- Test suite covering the plain, Django (including a live request through
  `RequestMiddleware`), and Celery entry points, plus rendered JSON output.

[0.3.0]: https://github.com/joelryan2k/opinionated-structlog-config/releases/tag/v0.3.0
[0.2.0]: https://github.com/joelryan2k/opinionated-structlog-config/releases/tag/v0.2.0
