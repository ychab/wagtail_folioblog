from django.utils.text import slugify
from django.utils.translation import get_language, to_locale

import factory
from factory import post_generation
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory

from folioblog.core.models import Menu, MenuLink

current_locale = to_locale(get_language())


class BaseCategoryFactory(DjangoModelFactory):

    class Meta:
        abstract = True
        django_get_or_create = ('slug',)

    name = factory.Faker('word', locale=current_locale)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))


class MenuFactory(DjangoModelFactory):

    class Meta:
        model = Menu

    homepage = factory.SubFactory(PageFactory)

    @post_generation
    def links(obj, create, extracted, **kwargs):
        if create:  # pragma: no branch
            number = kwargs.pop('number', 3)
            pages = [PageFactory() for i in range(0, number)]
            for page in pages:
                MenuLinkFactory(menu=obj, related_page=page, **kwargs)


class MenuLinkFactory(DjangoModelFactory):

    class Meta:
        model = MenuLink

    menu = factory.SubFactory(MenuFactory)
    related_page = factory.SubFactory(PageFactory)