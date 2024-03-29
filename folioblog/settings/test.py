from tempfile import gettempdir

from .base import *

INSTALLED_APPS += [
    # Well... @see https://github.com/wagtail/wagtail/issues/1824
    "wagtail.contrib.search_promotions",
]

EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

# Boost perf a little
PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

STATIC_ROOT = Path(gettempdir(), "folioblog", "static")
MEDIA_ROOT = Path(gettempdir(), "folioblog", "media")

WAGTAILADMIN_BASE_URL = "http://127.0.0.1:8000"

DEBUG_TEST = True
TEST_DEBUG_LOG = False

try:
    from .local import *
except ImportError:  # pragma: no cover
    pass

if TEST_DEBUG_LOG:  # pragma: no cover
    for logger in LOGGING["loggers"].values():
        logger["handlers"] = ["debug_file", "stream"]
        logger["level"] = "DEBUG"
    # Anyway, remove logging for migrations
    LOGGING["loggers"]["django.db.backends.schema"] = {
        "handlers": ["null"],
        "propagate": False,
    }
