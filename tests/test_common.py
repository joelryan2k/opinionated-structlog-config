"""Core behaviour in common.py: container detection, formatter, chain, sentry."""

from unittest import mock

import structlog

from opinionated_structlog_config import common


# --- is_running_in_container -------------------------------------------------


def test_not_in_container_when_cgroup_missing(monkeypatch):
    monkeypatch.setattr(common.os.path, "exists", lambda p: False)
    assert common.is_running_in_container() is False


def test_in_container_when_structlog_json_env_set(monkeypatch):
    monkeypatch.setattr(common.os.path, "exists", lambda p: True)
    monkeypatch.setenv("STRUCTLOG_JSON", "1")
    assert common.is_running_in_container() is True


def test_in_container_when_cgroup_mentions_docker(monkeypatch):
    monkeypatch.setattr(common.os.path, "exists", lambda p: True)
    monkeypatch.delenv("STRUCTLOG_JSON", raising=False)
    with mock.patch("builtins.open", mock.mock_open(read_data="1:name=systemd:/docker/abc")):
        assert common.is_running_in_container() is True


def test_in_container_when_cgroup_mentions_ecs(monkeypatch):
    monkeypatch.setattr(common.os.path, "exists", lambda p: True)
    monkeypatch.delenv("STRUCTLOG_JSON", raising=False)
    with mock.patch("builtins.open", mock.mock_open(read_data="9:cpuset:/ecs/task-id")):
        assert common.is_running_in_container() is True


def test_not_in_container_for_plain_cgroup(monkeypatch):
    monkeypatch.setattr(common.os.path, "exists", lambda p: True)
    monkeypatch.delenv("STRUCTLOG_JSON", raising=False)
    with mock.patch("builtins.open", mock.mock_open(read_data="0::/user.slice/session.scope")):
        assert common.is_running_in_container() is False


# --- build_formatter ---------------------------------------------------------


def test_build_formatter_uses_json_when_forced():
    fmt = common.build_formatter(force_json_output=True)
    assert fmt["()"] is structlog.stdlib.ProcessorFormatter
    assert isinstance(fmt["processor"], structlog.processors.JSONRenderer)


def test_build_formatter_uses_console_for_local_dev(monkeypatch):
    monkeypatch.setattr(common, "is_running_in_container", lambda: False)
    fmt = common.build_formatter(force_json_output=False)
    assert isinstance(fmt["processor"], structlog.dev.ConsoleRenderer)


def test_build_formatter_honours_container_detection(monkeypatch):
    monkeypatch.setattr(common, "is_running_in_container", lambda: True)
    fmt = common.build_formatter(force_json_output=False)
    assert isinstance(fmt["processor"], structlog.processors.JSONRenderer)


def test_build_formatter_foreign_pre_chain_present():
    fmt = common.build_formatter(force_json_output=True)
    pre_chain = fmt["foreign_pre_chain"]
    assert common.timestamper in pre_chain
    assert structlog.contextvars.merge_contextvars in pre_chain


# --- common_configure_structlog: the processor chain ------------------------


def test_configure_builds_expected_chain():
    common.common_configure_structlog({})
    cfg = structlog.get_config()
    processors = cfg["processors"]

    # First step merges contextvars, last hands off to the stdlib formatter.
    assert processors[0] is structlog.contextvars.merge_contextvars
    assert processors[-1] is structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    assert isinstance(cfg["logger_factory"], structlog.stdlib.LoggerFactory)


def test_configure_without_sentry_adds_no_sentry_processor():
    common.common_configure_structlog({})
    names = [type(p).__name__ for p in structlog.get_config()["processors"]]
    assert "SentryProcessor" not in names


# --- Sentry branch (init mocked, no network) --------------------------------


def test_sentry_branch_inits_sdk_and_adds_processor():
    config = {
        "SENTRY": {
            "DSN": "https://public@example.ingest.sentry.io/1",
            "OPTIONS": {"environment": "test", "traces_sample_rate": 0.25},
        }
    }
    with mock.patch("sentry_sdk.init") as init:
        common.common_configure_structlog(config)

    init.assert_called_once()
    _, kwargs = init.call_args
    assert kwargs["dsn"] == config["SENTRY"]["DSN"]
    assert kwargs["environment"] == "test"
    assert kwargs["traces_sample_rate"] == 0.25

    names = [type(p).__name__ for p in structlog.get_config()["processors"]]
    assert "SentryProcessor" in names


def test_sentry_defaults_include_local_variables_to_false():
    config = {"SENTRY": {"DSN": "https://public@example.ingest.sentry.io/1"}}
    with mock.patch("sentry_sdk.init") as init:
        common.common_configure_structlog(config)

    _, kwargs = init.call_args
    assert kwargs["include_local_variables"] is False


def test_sentry_options_can_override_include_local_variables():
    config = {
        "SENTRY": {
            "DSN": "https://public@example.ingest.sentry.io/1",
            "OPTIONS": {"include_local_variables": True},
        }
    }
    with mock.patch("sentry_sdk.init") as init:
        common.common_configure_structlog(config)

    _, kwargs = init.call_args
    assert kwargs["include_local_variables"] is True
