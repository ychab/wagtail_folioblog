from django.utils.text import slugify
from django.utils.translation import get_language, to_locale

from wagtail.models import Site

import factory
from factory.django import DjangoModelFactory
from taggit.models import Tag

current_locale = to_locale(get_language())


class BaseTagFactory(DjangoModelFactory):
    class Meta:
        abstract = True
        django_get_or_create = ("slug",)
        skip_postgeneration_save = True

    name = factory.Faker("word", locale=current_locale)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    site = factory.LazyFunction(lambda: Site.objects.get(is_default_site=True))


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ("slug",)

    name = factory.Faker("word", locale=current_locale)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
