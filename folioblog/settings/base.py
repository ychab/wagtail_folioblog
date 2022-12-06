"""
Django settings for folioblog project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from tempfile import gettempdir

from django.utils.log import DEFAULT_LOGGING

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
DEBUG = False
DEBUG_TEST = False
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # Must be before "wagtail.users" at least
    # @see https://docs.wagtail.org/en/stable/advanced_topics/customisation/custom_user_models.html#custom-user-models
    'folioblog.user',

    'wagtail.contrib.modeladmin',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.settings',
    'wagtail.contrib.sitemaps',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'modelcluster',
    'taggit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.postgres',
    'django.contrib.sitemaps',

    'django_social_share',
    'compressor',

    'folioblog.core',
    'folioblog.video',
    'folioblog.blog',
    'folioblog.portfolio',
    'folioblog.search',
    'folioblog.home',
    'folioblog.gallery',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'folioblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'wagtail.contrib.settings.context_processors.settings',

                'folioblog.core.context_processors.menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'folioblog.wsgi.application'

AUTH_USER_MODEL = 'user.User'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

# Yeah mama, I don't want to do "frenglish" so I keep FR as source language ;-)
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)
FORMAT_MODULE_PATH = [
    'folioblog.formats',
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'compressor.finders.CompressorFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

COMPRESS_ENABLED = False
COMPRESS_OFFLINE = True
COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_OFFLINE_CONTEXT = {}
COMPRESS_FILTERS = {
    'css': [
        # Use defaults (yuglify+cssmin broke url('data:uri'), clean-css-cli good but no gain)
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.rCSSMinFilter',
    ],
    'js': [
        # Trusts uglify-js from source instead of old wrapper Yuglify
        'folioblog.core.compressor.UglifyJSFilter',
    ],
}

LOGGING = DEFAULT_LOGGING.copy()
# Define an handler for debugging (purpose dev or prod)
LOGGING['formatters']['debug'] = {
    'format': '[%(levelname)s][%(name)s][%(asctime)s][%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s',
}
LOGGING['handlers']['debug_file'] = {
    'level': 'DEBUG',
    'class': 'logging.FileHandler',
    'filename': os.path.join(gettempdir(), 'folioblog-debug.log'),
    'formatter': 'debug',
}
LOGGING['handlers']['null'] = {
    'class': 'logging.NullHandler',
}
LOGGING['handlers']['stream'] = {
    'level': 'INFO',
    'class': 'logging.StreamHandler',
}
LOGGING['loggers']['folioblog'] = {
    'handlers': ['console', 'mail_admins'],
    'level': 'INFO',
}
LOGGING['loggers']['folioblog']['profiling'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Wagtail settings

WAGTAIL_SITE_NAME = "Portfolio blog"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}

WAGTAILADMIN_RICH_TEXT_EDITORS = {
    'default': {
        'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
        'OPTIONS': {
            'features': [
                'bold', 'italic', 'h2', 'h3', 'h4', 'ol', 'ul', 'hr',
                'link', 'document-link', 'image', 'embed',
                'code', 'blockquote', 'superscript' , 'subscript', 'strikethrough',
                'keyboard',
            ]
        }
    },
}

WAGTAIL_PASSWORD_MANAGEMENT_ENABLED = False

WAGTAILIMAGES_IMAGE_MODEL = 'core.FolioImage'
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # i.e. 20MB, check WSGI + frontend
WAGTAILIMAGES_WEBP_QUALITY = 100  # we want the best dude!
WAGTAILIMAGES_JPEG_QUALITY = 100
WAGTAILIMAGES_FORMAT_CONVERSIONS = {
    'bmp': 'jpeg',
    'webp': 'webp',  # be player! better quality and very lighter than PNG!!
}
WAGTAIL_USAGE_COUNT_ENABLED = True

WAGTAIL_DATE_FORMAT = '%d/%m/%Y'
WAGTAIL_DATETIME_FORMAT = '%d/%m/%Y %H:%M'
WAGTAIL_TIME_FORMAT = '%H:%M'

TAGGIT_CASE_INSENSITIVE = True

FOLIOBLOG_COMPRESSOR_UGLIFY_BINARY = os.path.join(BASE_DIR, 'node_modules', 'uglify-js', 'bin', 'uglifyjs')
FOLIOBLOG_COMPRESSOR_UGLIFY_ARGUMENTS = ''