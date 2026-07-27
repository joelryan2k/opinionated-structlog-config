"""The plain (non-Django) entry point: configure_for_structlog."""

import logging

import structlog

import opinionated_structlog_config


def _root_handler_renderer():
    root = logging.getLogger()
    (handler,) = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
    # ProcessorFormatter keeps the renderer as the last entry in .processors.
    return handler.formatter.processors[-1]


def test_configure_installs_single_console_handler_and_configures_structlog():
    opinionated_structlog_config.configure_for_structlog(force_json_output=True)

    root = logging.getLogger()
    stream_handlers = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
    assert len(stream_handlers) == 1
    assert root.level == logging.INFO
    assert structlog.is_configured()


def test_configure_forces_json_renderer_when_requested():
    opinionated_structlog_config.configure_for_structlog(force_json_output=True)
    assert isinstance(_root_handler_renderer(), structlog.processors.JSONRenderer)


def test_configure_uses_console_renderer_for_local_dev(monkeypatch):
    monkeypatch.setattr(
        "opinionated_structlog_config.common.is_running_in_container", lambda: False
    )
    opinionated_structlog_config.configure_for_structlog(force_json_output=False)
    assert isinstance(_root_handler_renderer(), structlog.dev.ConsoleRenderer)


def test_configure_accepts_config_dict():
    # A bare config with no SENTRY key must not blow up.
    opinionated_structlog_config.configure_for_structlog(config={})
    assert structlog.is_configured()
