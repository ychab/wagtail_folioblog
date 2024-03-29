from django.conf import settings
from django.utils.translation import get_language, to_locale

from wagtail.models import Locale, Site

import factory
import wagtail_factories
from factory import fuzzy
from factory.django import DjangoModelFactory

from folioblog.core.factories import (
    CookieBannersBlockFactory,
    PageNotFoundsBlockFactory,
    RssFeedsBlockFactory,
)
from folioblog.core.models import FolioBlogSettings

current_locale = to_locale(get_language())


class LocaleFactory(DjangoModelFactory):
    class Meta:
        model = Locale
        django_get_or_create = ("language_code",)
        skip_postgeneration_save = True

    language_code = fuzzy.FuzzyChoice(list(dict(settings.LANGUAGES).keys()))


class FolioBlogSettingsFactory(DjangoModelFactory):
    class Meta:
        model = FolioBlogSettings
        skip_postgeneration_save = True
        django_get_or_create = ("site",)

    site = factory.LazyFunction(lambda: Site.objects.get(is_default_site=True))

    cookie_banner = wagtail_factories.StreamFieldFactory(CookieBannersBlockFactory)
    rss_feed = wagtail_factories.StreamFieldFactory(RssFeedsBlockFactory)
    text_404 = wagtail_factories.StreamFieldFactory(PageNotFoundsBlockFactory)
