from django.db import models
from django.db.models import QuerySet
from django.utils.translation import get_language

from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class I18nQuerySetMixin:

    def filter_language(self, language_code=None):
        language_code = language_code or get_language()
        return self.filter(locale__language_code=language_code)

    def filter_locale(self, locale):
        return self.filter(locale=locale)


class I18nQuerySet(I18nQuerySetMixin, QuerySet):
    pass


class I18nPageQuerySet(I18nQuerySetMixin, PageQuerySet):
    pass


class ImageManager(models.Manager):
    def get_queryset(self):
        return self._queryset_class(self.model).select_related('photographer')


class ImagePageManager(PageManager):

    def get_queryset(self):
        return self._queryset_class(self.model) \
            .select_related('image__photographer') \
            .prefetch_related('image__renditions')


I18nManager = models.Manager.from_queryset(I18nQuerySet)
I18nPageManager = PageManager.from_queryset(I18nPageQuerySet)
I18nIndexPageManager = ImagePageManager.from_queryset(I18nPageQuerySet)
