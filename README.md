# Basic config

settings.py

```
import django_structlog_config
LOGGING = django_structlog_config.configure_app_for_structlog(MIDDLEWARE)
```

# Celery

settings.py

```
DJANGO_STRUCTLOG_CELERY_ENABLED = True
```

celery.py

```
from django_structlog_config.celery import configure_celery_for_structlog
configure_celery_for_structlog(app)
```
