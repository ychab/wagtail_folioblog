from django.conf import settings
from django.utils.translation import get_language, to_locale

import factory
import wagtail_factories
from factory import fuzzy

from folioblog.core.blocks import (
    CookieBannerBlock, CookieBannersBlock, RssFeedBlock, RssFeedsBlock,
)

current_locale = to_locale(get_language())


class CookieBannerBlockFactory(wagtail_factories.StructBlockFactory):

    class Meta:
        model = CookieBannerBlock

    language = fuzzy.FuzzyChoice(list(dict(settings.LANGUAGES).keys()))

    title = factory.Faker('sentence', nb_words=5, locale=current_locale)
    text = factory.Faker('text', locale=current_locale)

    page = factory.SubFactory(wagtail_factories.PageChooserBlockFactory)
    link_text = factory.Faker('sentence', nb_words=5, locale=current_locale)

    button_cancel_text = factory.Faker('word', locale=current_locale)
    button_accept_text = factory.Faker('word', locale=current_locale)


class CookieBannersBlockFactory(wagtail_factories.StreamBlockFactory):

    class Meta:
        model = CookieBannersBlock

    banners = factory.SubFactory(CookieBannerBlockFactory)


class RssFeedBlockFactory(wagtail_factories.StructBlockFactory):

    class Meta:
        model = RssFeedBlock

    language = fuzzy.FuzzyChoice(list(dict(settings.LANGUAGES).keys()))

    title = factory.Faker('sentence', nb_words=5, locale=current_locale)
    description = factory.Faker('text', locale=current_locale)
    limit = fuzzy.FuzzyInteger(3, 6)


class RssFeedsBlockFactory(wagtail_factories.StreamBlockFactory):

    class Meta:
        model = RssFeedsBlock

    feeds = factory.SubFactory(RssFeedBlockFactory)
