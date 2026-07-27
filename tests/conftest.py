"""Shared fixtures.

The library configures the *root* logger and the global structlog defaults as
process-wide side effects. These fixtures isolate each test from the next and
give tests a way to capture what actually gets rendered to a handler.
"""

import io
import json
import logging

import pytest
import structlog

from opinionated_structlog_config.common import (
    build_formatter,
    common_configure_structlog,
)


@pytest.fixture(autouse=True)
def _isolate_logging(monkeypatch):
    """Snapshot/restore global logging + structlog state around every test."""
    monkeypatch.delenv("STRUCTLOG_JSON", raising=False)
    structlog.contextvars.clear_contextvars()

    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level

    yield

    root.handlers[:] = saved_handlers
    root.setLevel(saved_level)
    structlog.reset_defaults()
    structlog.contextvars.clear_contextvars()


class LogCapture:
    """Attaches a real ProcessorFormatter handler to root and reads it back."""

    def __init__(self, stream):
        self._stream = stream

    def lines(self):
        return [ln for ln in self._stream.getvalue().splitlines() if ln.strip()]

    def json_records(self):
        """Parse each captured line as JSON (JSON-mode output only)."""
        return [json.loads(ln) for ln in self.lines()]


@pytest.fixture
def capture():
    """Configure structlog + a JSON-rendering root handler, capture output.

    Returns a callable ``setup(config=None, force_json=True)`` that wires
    everything up exactly the way the library does (same processor chain, same
    ProcessorFormatter) and returns a ``LogCapture``.
    """

    def _setup(config=None, force_json=True):
        common_configure_structlog(config or {})

        formatter_dict = dict(build_formatter(force_json_output=force_json))
        factory = formatter_dict.pop("()")
        formatter = factory(**formatter_dict)

        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)

        root = logging.getLogger()
        root.addHandler(handler)
        root.setLevel(logging.DEBUG)

        return LogCapture(stream)

    return _setup
