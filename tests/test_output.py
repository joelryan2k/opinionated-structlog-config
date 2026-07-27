"""What actually lands in the logs: JSON shape, contextvars, exceptions."""

import logging

import structlog


def test_json_line_has_expected_shape(capture):
    cap = capture()  # force_json=True

    structlog.get_logger("some.logger").info("an_event", customer_id=42)

    records = cap.json_records()
    assert len(records) == 1
    record = records[0]
    assert record["event"] == "an_event"
    assert record["level"] == "info"
    assert record["logger"] == "some.logger"
    assert record["customer_id"] == 42
    assert "timestamp" in record  # ISO timestamper


def test_bound_contextvars_appear_in_output(capture):
    cap = capture()

    structlog.contextvars.bind_contextvars(request_id="req-abc", correlation_id="corr-xyz")
    structlog.get_logger("ctx").info("with_context")

    record = cap.json_records()[0]
    assert record["request_id"] == "req-abc"
    assert record["correlation_id"] == "corr-xyz"


def test_debug_dropped_at_info_root_level(capture):
    cap = capture()
    # The library's opinionated root level is INFO; assert filter_by_level honours it.
    logging.getLogger().setLevel(logging.INFO)

    log = structlog.get_logger("levels")
    log.debug("should_not_appear")
    log.warning("should_appear")

    events = [r["event"] for r in cap.json_records()]
    assert "should_appear" in events
    assert "should_not_appear" not in events


def test_exception_info_is_rendered(capture):
    cap = capture()

    log = structlog.get_logger("boom")
    try:
        raise ValueError("kaboom")
    except ValueError:
        log.exception("it_failed")

    record = cap.json_records()[0]
    assert record["event"] == "it_failed"
    assert record["level"] == "error"
    assert "kaboom" in record["exception"]
