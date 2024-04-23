# Basic config

settings.py

```
import opinionated_structlog_config
opinionated_structlog_config.configure_for_structlog(MIDDLEWARE)
```
# Django

settings.py

```
import opinionated_structlog_config.django
LOGGING = opinionated_structlog_config.configure_django_for_structlog(MIDDLEWARE)
```

# Celery

settings.py

```
DJANGO_STRUCTLOG_CELERY_ENABLED = True
```

celery.py

```
from opinionated_structlog_config.celery import configure_celery_for_structlog
configure_celery_for_structlog(app)
```
