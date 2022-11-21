# @see https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/
from .base import *

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# For Django back-office, enable SSL if needed
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True  # Just in case, should be done by webserver instead

COMPRESS_ENABLED = True

# Cache per site: will cache all pages by their full GET url
MIDDLEWARE.insert(0, 'folioblog.core.middleware.AnonymousUpdateCacheMiddleware')  # Must be FIRST to be latest!
MIDDLEWARE.append('folioblog.core.middleware.AnonymousFetchCacheMiddleware')

# By default, all children of 'django' logger will inherit the handlers
# console + mail_admins. However, console is not enable if DEBUG = False!
# That's why we append the 'django.server' handler, which is just a StreamHandler.
# Then we capture the stdout/stderr to log it with the WSGI server instead.
for logger in LOGGING['loggers'].values():
    if 'django.server' not in logger['handlers']:
        logger['handlers'] += ['django.server']

try:
    from .local import *
except ImportError:
    pass
