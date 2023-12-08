import os

def load_secret(filepath):
    try:
        with open(filepath, mode="r") as fp:
            return fp.read()
    except Exception:  # Better ask for forgiveness than permission!
        pass


def load_secret_key():
    secret_key = load_secret(os.getenv("FOLIOBLOG_SECRET_KEY_FILE"))
    if not secret_key:
        # Fallback just for building image with a dummy key.
        secret_key = os.getenv("FOLIOBLOG_SECRET_KEY_DUMMY")
    return secret_key


SECRET_KEY = load_secret_key()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("FOLIOBLOG_POSTGRES_DB"),
        "USER": os.getenv("FOLIOBLOG_POSTGRES_USER"),
        "PASSWORD": load_secret(os.getenv("FOLIOBLOG_POSTGRES_PASSWORD_FILE")),
        "HOST": os.getenv("FOLIOBLOG_POSTGRES_HOST"),
        "PORT": int(os.getenv("FOLIOBLOG_POSTGRES_PORT", 5432)),
    }
}

LANGUAGE_CODE = os.getenv("FOLIOBLOG_LANGUAGE_CODE")
TIME_ZONE = os.getenv("FOLIOBLOG_TIME_ZONE", "Europe/Paris")

# Folio settings
ADMIN_PASSWORD = load_secret(os.getenv("FOLIOBLOG_ADMIN_PASSWD_FILE"))

# Wagtail settings
WAGTAIL_SITE_NAME = os.getenv("FOLIOBLOG_SITE_NAME")
WAGTAILADMIN_BASE_URL = os.getenv("FOLIOBLOG_BASE_URL")
WAGTAILAPI_BASE_URL = WAGTAILADMIN_BASE_URL

# Basics
ALLOWED_HOSTS = eval(os.getenv("FOLIOBLOG_ALLOWED_HOSTS", "[]"))
ADMINS = eval(os.getenv("FOLIOBLOG_ADMINS", "()"))
MANAGERS = ADMINS

# Medias
STATIC_ROOT = os.getenv("FOLIOBLOG_STATIC_ROOT")
MEDIA_ROOT = os.getenv("FOLIOBLOG_MEDIA_ROOT")

# Emails
DEFAULT_FROM_EMAIL = os.getenv("FOLIOBLOG_DEFAULT_FROM_EMAIL")
SERVER_EMAIL = os.getenv("FOLIOBLOG_SERVER_EMAIL")
EMAIL_USE_TLS = eval(os.getenv("FOLIOBLOG_EMAIL_USE_TLS", "True"))
EMAIL_HOST = os.getenv("FOLIOBLOG_EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("FOLIOBLOG_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = load_secret(os.getenv("FOLIOBLOG_EMAIL_HOST_PASSWORD_FILE"))
EMAIL_PORT = int(os.getenv("FOLIOBLOG_EMAIL_PORT", 587))

# Security
CSRF_COOKIE_SECURE = eval(os.getenv("FOLIOBLOG_CSRF_COOKIE_SECURE", "True"))
SESSION_COOKIE_SECURE = eval(os.getenv("FOLIOBLOG_SESSION_COOKIE_SECURE", "True"))
SECURE_SSL_REDIRECT = eval(os.getenv("FOLIOBLOG_SECURE_SSL_REDIRECT", "True"))
SECURE_PROXY_SSL_HEADER = eval(os.getenv("FOLIOBLOG_HTTP_X_FORWARDED_PROTO", "None"))
USE_X_FORWARDED_HOST = eval(os.getenv("FOLIOBLOG_USE_X_FORWARDED_HOST", "False"))

# Cache
redis_location = os.getenv("FOLIOBLOG_REDIS_LOCATION")
if redis_location:
    redis_user = os.getenv("FOLIOBLOG_REDIS_USER", "default")
    redis_password = load_secret(os.getenv("FOLIOBLOG_REDIS_PASSWORD_FILE"))

    scheme, location = redis_location.split("://")
    redis_location = f"{scheme}://{redis_user}:{redis_password}@{location}"

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": redis_location,
            "KEY_PREFIX": os.getenv("FOLIOBLOG_REDIS_KEY_PREFIX"),
            "TIMEOUT": int(os.getenv("FOLIOBLOG_REDIS_TIMEOUT", 86400)),
        },
    }
    CACHE_MIDDLEWARE_SECONDS = int(os.getenv("FOLIOBLOG_CACHE_MIDDLEWARE_SECONDS", 86400))
