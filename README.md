# Basic config

settings.py

```
import opinionated_structlog_config
opinionated_structlog_config.configure_for_structlog()
```
# Django

settings.py

```
import opinionated_structlog_config.django
LOGGING = opinionated_structlog_config.django.configure_django_for_structlog(MIDDLEWARE)
```

# Celery

celery.py

```
from opinionated_structlog_config.celery import configure_celery_for_structlog
configure_celery_for_structlog(app)
```

# Sentry

OPINIONATED_STRUCTLOG_CONFIG = {
    'SENTRY': {
        'DSN': '<dsn>',
        'OPTIONS': {
            'traces_sample_rate': sentry_rate,
            'profiles_sample_rate': sentry_rate,
            'environment': sentry_env,
        }
    }
}

# Anything in OPTIONS is passed straight to sentry_sdk.init(). Sentry defaults to
# include_local_variables=False here; override it in OPTIONS if you want locals
# attached to stack frames.

import opinionated_structlog_config.django
LOGGING = opinionated_structlog_config.django.configure_django_for_structlog(MIDDLEWARE, config=OPINIONATED_STRUCTLOG_CONFIG)