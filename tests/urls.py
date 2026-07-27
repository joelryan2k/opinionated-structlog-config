"""URLconf for the live-request Django test."""

import structlog
from django.http import HttpResponse
from django.urls import path


def index(request):
    # Uses a logger fetched at call time so it picks up the per-test config.
    structlog.get_logger("tests.view").info("hello_from_view")
    return HttpResponse("ok")


urlpatterns = [
    path("", index),
]
