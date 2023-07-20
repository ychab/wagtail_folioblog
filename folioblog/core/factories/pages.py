from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import get_language, to_locale

from wagtail.models import Site
from wagtail.rich_text import RichText

import factory
import wagtail_factories
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker
from wagtail_factories import PageFactory

from folioblog.core.factories import ImageFactory
from folioblog.core.models import BasicPage, BasicPageRelatedLink

User = get_user_model()
current_locale = to_locale(get_language())
fake = Faker(locale=current_locale)


class BaseIndexPageFactory(wagtail_factories.PageFactory):

    class Meta:
        abstract = True
        skip_postgeneration_save = True

    parent = factory.LazyFunction(lambda: Site.objects.get(is_default_site=True).root_page)

    title = factory.Sequence(lambda n: 'page_{n}'.format(n=n))
    slug = factory.LazyAttribute(lambda o: slugify(o.title))

    subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)
    image = factory.SubFactory(ImageFactory)
    image_alt = factory.Faker('sentence', nb_words=5, locale=current_locale)

    first_published_at = fuzzy.FuzzyDateTime(
        start_dt=timezone.now() - timedelta(days=10),
        end_dt=timezone.now(),
    )
    last_published_at = fuzzy.FuzzyDateTime(
        start_dt=timezone.now() + timedelta(days=5),
        end_dt=timezone.now() + timedelta(days=10),
    )


class BasePageFactory(BaseIndexPageFactory):

    class Meta:
        abstract = True

    parent = None  # Children MUST set parent
    intro = factory.Faker('paragraph', locale=current_locale)
    body = factory.LazyFunction(lambda: RichText(fake.text()))  # @todo - RickTextBlockFactory()


class BasicPageRelatedLinkFactory(DjangoModelFactory):

    class Meta:
        model = BasicPageRelatedLink
        skip_postgeneration_save = True

    page = factory.SubFactory('folioblog.core.factories.BasicPageFactory')
    related_page = factory.SubFactory(PageFactory)


class BasicPageFactory(BasePageFactory):

    class Meta:
        model = BasicPage

    @factory.post_generation
    def related_pages(obj, create, extracted, **kwargs):
        if create:  # pragma: nobranch
            related_pages = []

            if extracted:
                related_pages = extracted
            elif kwargs.get('number', 0) > 0:
                related_pages = [
                    BasicPageFactory(parent=obj.get_parent()) for i in range(0, kwargs['number'])
                ]

            for page in related_pages:
                BasicPageRelatedLinkFactory(page=obj, related_page=page)
