"""Celery entry point: worker step registration and correlation_id binding."""

import structlog
from celery import Celery
from django_structlog.celery.steps import DjangoStructLogInitStep

import opinionated_structlog_config.celery as osc_celery


def test_configure_celery_registers_worker_init_step():
    app = Celery("test-app")

    osc_celery.configure_celery_for_structlog(app)

    assert DjangoStructLogInitStep in app.steps["worker"]


class _FakeRequest:
    correlation_id = "corr-123"


class _FakeTask:
    request = _FakeRequest()


def test_bind_extra_task_metadata_binds_correlation_id():
    osc_celery.receiver_bind_extra_request_metadata(
        sender=None, signal=None, task=_FakeTask()
    )

    assert structlog.contextvars.get_contextvars()["correlation_id"] == "corr-123"


def test_bound_correlation_id_shows_up_in_task_logs(capture):
    cap = capture()

    osc_celery.receiver_bind_extra_request_metadata(
        sender=None, signal=None, task=_FakeTask()
    )
    structlog.get_logger("celery.task").info("task_running")

    record = cap.json_records()[0]
    assert record["correlation_id"] == "corr-123"
