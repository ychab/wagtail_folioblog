from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "wagtail.contrib.styleguide",
    "django_extensions",
    "debug_toolbar",
]

INTERNAL_IPS = ("127.0.0.1",)
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

for logger in LOGGING["loggers"].values():
    logger["handlers"] = ["console"]
    logger["level"] = "DEBUG"

AUTH_PASSWORD_VALIDATORS = []

WAGTAILADMIN_BASE_URL = "http://127.0.0.1:8000"
WAGTAILAPI_BASE_URL = WAGTAILADMIN_BASE_URL

try:
    from .local import *
except ImportError:
    pass
