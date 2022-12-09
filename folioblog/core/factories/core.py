from django.conf import settings
from django.utils.translation import get_language, to_locale

from wagtail.models import Locale

import wagtail_factories
from factory import fuzzy
from factory.django import DjangoModelFactory

from folioblog.core.factories import (
    CookieBannersBlockFactory, RssFeedsBlockFactory,
)
from folioblog.core.models import FolioBlogSettings

current_locale = to_locale(get_language())


class LocaleFactory(DjangoModelFactory):

    class Meta:
        model = Locale
        django_get_or_create = ('language_code',)

    language_code = fuzzy.FuzzyChoice(list(dict(settings.LANGUAGES).keys()))


class FolioBlogSettingsFactory(DjangoModelFactory):

    class Meta:
        model = FolioBlogSettings

    cookie_banner = wagtail_factories.StreamFieldFactory(CookieBannersBlockFactory)
    rss_feed = wagtail_factories.StreamFieldFactory(RssFeedsBlockFactory)
