# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## What this is

`opinionated-structlog-config` is a small distributable library that gives Python/Django/Celery apps a single-call, batteries-included [structlog](https://www.structlog.org/) setup. Downstream projects import it from their `settings.py` / `celery.py` and get consistent structured logging without hand-assembling processor chains.

## Commands

Poetry-managed project, run through [devbox](https://www.jetify.com/devbox). Dependencies live in `pyproject.toml` / `poetry.lock`; the toolchain (Python, Poetry) is pinned in `devbox.json`. Preface every command with `devbox run` so it executes inside the devbox environment.

```bash
devbox run poetry install --all-extras --with dev   # extras + test tooling (pytest, celery)
devbox run poetry run pytest                         # run the test suite
devbox run poetry run pytest tests/test_django.py::test_configure_appends_middleware_and_returns_logging   # run a single test
```

The test suite lives in `tests/` and needs the `dev` group (pytest, pytest-django) plus every extra installed; `pytest-django` is pointed at `tests.settings` via `[tool.pytest.ini_options]`.

The optional extras (`django`, `sentry`, `celery`) gate the heavy dependencies. Code that touches `django.py` or the Sentry branch of `common.py` only imports those packages lazily/inside functions, so the base install stays light — preserve that pattern when editing. (`celery.py` is the exception: it imports `celery`/`django_structlog.celery`/`django.conf.settings` at module level, so it requires the `celery` extra to import at all.)

## Releasing & versioning

For any change that affects consumers (skip for tests/CI/internal-docs-only changes), do all three:

1. Bump `version` in `pyproject.toml` per [SemVer](https://semver.org/). Pre-1.0: breaking → minor (`0.2.0` → `0.3.0`), otherwise patch (`0.2.0` → `0.2.1`).
2. Add a `## [x.y.z] - YYYY-MM-DD` section to the top of `CHANGELOG.md` ([Keep a Changelog](https://keepachangelog.com/) format), plus the `[x.y.z]: .../releases/tag/vx.y.z` link at the bottom. Prefix breaking changes with `BREAKING:` and state the required consumer action.
3. Tag and push: `git tag vX.Y.Z && git push origin main --tags`.

## Architecture

Three entry points, one shared core. Every public function funnels through `common.py`, which owns the actual structlog processor chain and the console-vs-JSON formatter decision.

- **`common.py`** — the core. `common_configure_structlog(config)` builds the `structlog.configure(...)` processor chain. `build_formatter(force_json_output)` returns a `logging` dictConfig formatter dict wrapping either `JSONRenderer` (prod) or `ConsoleRenderer` (dev). `_configure_sentry` / the `SENTRY` config branch are optional and only import `sentry_sdk` + `structlog_sentry` when a `SENTRY` key is present in the passed config.
- **`__init__.py`** — `configure_for_structlog(...)` for a plain (non-Django) app. Applies a `logging.config.dictConfig` with a single console handler at root.
- **`django.py`** — `configure_django_for_structlog(middleware, config)`. Mutates the passed `MIDDLEWARE` list (appends `django_structlog.middlewares.RequestMiddleware`) and **returns** the dict the caller assigns to `LOGGING`.
- **`celery.py`** — `configure_celery_for_structlog(app)` plus module-level Celery signal receivers (`setup_logging`, `bind_extra_task_metadata`) that reconfigure logging inside workers and bind `correlation_id` into contextvars. Reads config from `settings.OPINIONATED_STRUCTLOG_CONFIG`.

### Console-vs-JSON auto-detection

The key opinionated behavior lives in `common.is_running_in_container()`. Output is JSON when running in a container (detected via `/proc/self/cgroup` containing `containerd`/`docker`/`/ecs/`) or when the `STRUCTLOG_JSON` env var is set; otherwise it renders pretty console output for local dev. `force_json_output=True` overrides detection. When changing rendering logic, this function is the single source of truth.

### Config object

All entry points accept an optional `config` dict. The only recognized key today is `SENTRY` (`{'DSN': ..., 'OPTIONS': {...}}`). Django/Celery consumers pass it via the `OPINIONATED_STRUCTLOG_CONFIG` Django setting; see `README.md` for the exact shape.
