from tempfile import gettempdir

from .base import *

INSTALLED_APPS += [
    # Well... @see https://github.com/wagtail/wagtail/issues/1824
    'wagtail.contrib.search_promotions',
]

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Boost perf a little
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

STATIC_ROOT = os.path.join(gettempdir(), 'folioblog', 'static')
MEDIA_ROOT = os.path.join(gettempdir(), 'folioblog', 'media')

WAGTAILADMIN_BASE_URL = 'http://127.0.0.1:8000'
WAGTAILAPI_BASE_URL = WAGTAILADMIN_BASE_URL

DEBUG_TEST = True
DEBUG_LOG = False

TEST_SELENIUM_HUB = False

try:
    from .local import *
except ImportError:  # pragma: no cover
    pass

if DEBUG_LOG:  # pragma: no cover
    for logger in LOGGING['loggers'].values():
        logger['handlers'] = ['debug_file']
        logger['level'] = 'DEBUG'
    # Anyway, remove logging for migrations
    LOGGING['loggers']['django.db.backends.schema'] = {
        'handlers': ['null'],
        'propagate': False,
    }
