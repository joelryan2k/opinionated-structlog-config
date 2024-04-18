# Basic config

settings.py

```
import structured_logging_config
LOGGING = structured_logging_config.configure_app_for_structlog(MIDDLEWARE)
```

# Celery

settings.py

```
DJANGO_STRUCTLOG_CELERY_ENABLED = True
```

celery.py

```
from structured_logging_config.celery import configure_celery_for_structlog
configure_celery_for_structlog(app)
```
