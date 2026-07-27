"""Django entry point, including a real request through RequestMiddleware."""

import structlog

import opinionated_structlog_config.django as osc_django


def test_configure_appends_middleware_and_returns_logging():
    middleware = ["myapp.middleware.Something"]

    logging_dict = osc_django.configure_django_for_structlog(middleware)

    # Mutates the passed list in place...
    assert middleware[-1] == "django_structlog.middlewares.RequestMiddleware"
    # ...and returns the dictConfig the caller assigns to LOGGING.
    assert logging_dict["version"] == 1
    assert logging_dict["root"]["level"] == "INFO"
    assert logging_dict["root"]["handlers"] == ["console"]
    assert "console_formatter" in logging_dict["formatters"]
    # structlog is configured as a side effect.
    assert structlog.is_configured()


def test_configure_passes_config_through_to_sentry(monkeypatch):
    called = {}

    def fake_configure(config):
        called["config"] = config

    monkeypatch.setattr(osc_django, "common_configure_structlog", fake_configure)

    config = {"SENTRY": {"DSN": "https://x@example.sentry.io/1"}}
    osc_django.configure_django_for_structlog([], config=config)

    assert called["config"] is config


def test_live_request_emits_request_id_in_json_logs(client, capture):
    # Wire up structlog + a JSON-capturing root handler the same way the
    # library does, then drive a real request through RequestMiddleware.
    cap = capture()

    response = client.get("/")
    assert response.status_code == 200

    records = cap.json_records()
    by_event = {r.get("event"): r for r in records}

    # django_structlog's middleware logs these with a bound request_id.
    assert "request_started" in by_event
    assert "request_finished" in by_event
    request_id = by_event["request_started"]["request_id"]
    assert request_id

    # The view's own log call inherits the same request_id via contextvars.
    assert by_event["hello_from_view"]["request_id"] == request_id
