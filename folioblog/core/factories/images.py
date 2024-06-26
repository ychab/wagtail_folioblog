from django.utils.translation import get_language, to_locale

from wagtail.images import get_image_model
from wagtail.models import Site

import factory
import wagtail_factories
from factory.django import DjangoModelFactory

from folioblog.core.models import Photographer

current_locale = to_locale(get_language())
Image = get_image_model()


class PhotographerFactory(DjangoModelFactory):
    class Meta:
        model = Photographer
        skip_postgeneration_save = True

    name = factory.Faker("name", locale=current_locale)
    website = factory.Faker("url", locale=current_locale)
    site = factory.LazyFunction(lambda: Site.objects.get(is_default_site=True))


class ImageFactory(wagtail_factories.ImageFactory):
    file = factory.django.ImageField(filename="fake-image.webp", format="WEBP")
    caption = factory.Faker("sentence", nb_words=5, variable_nb_words=False, locale=current_locale)
    photographer = factory.SubFactory(PhotographerFactory)

    class Meta:
        skip_postgeneration_save = True

    @factory.post_generation
    def tags(obj, create, extracted, **kwargs):
        if create and extracted:  # pragma: no branch
            obj.tags.set(extracted)
