# @see https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
from .base import *

# For Django back-office, enable SSL if needed
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True  # Just in case, should be done by webserver instead

COMPRESS_ENABLED = True

# By default, all children of 'django' logger will inherit the handlers
# console + mail_admins. However, console is not enable if DEBUG is False!
# That's why we append the 'django.server' handler, which is just a StreamHandler.
# Then we capture the stdout/stderr to log it with the WSGI server instead.
for logger in LOGGING["loggers"].values():
    if "django.server" not in logger["handlers"]:
        logger["handlers"] += ["django.server"]

try:
    from .local import *
except ImportError:
    pass

if "CACHES" in locals():
    # Cache per site: will cache all pages by their full GET url
    MIDDLEWARE.insert(0, "folioblog.core.middleware.AnonymousUpdateCacheMiddleware")
    MIDDLEWARE.append("folioblog.core.middleware.AnonymousFetchCacheMiddleware")
