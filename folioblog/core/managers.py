from django.db import models
from django.db.models import Q, QuerySet
from django.utils.translation import get_language

from wagtail.models import PageManager
from wagtail.query import PageQuerySet


def qs_in_site_alt(qs, site):
    """
    Filter on ALL lang derivative root pages of a site.
    """
    q = Q()

    root_pages = site.root_page.get_translations(inclusive=True)
    for root_page in root_pages:
        # Mimic descendant_of(inclusive=True), but combine them.
        q |= Q(path__startswith=root_page.path) & Q(depth__gte=root_page.depth)

    return qs.filter(q)


class I18nQuerySetMixin:
    def filter_language(self, language_code=None):
        language_code = language_code or get_language()
        return self.filter(locale__language_code=language_code)

    def filter_locale(self, locale):
        return self.filter(locale=locale)

    # def in_site_alt(self, site):
    #     return qs_in_site_alt(self, site)
    #
    def in_site_locale(self, site, locale):
        return self.descendant_of(site.root_page.get_translation(locale))

    def in_site_localized(self, site):
        # in_site() seems to be buggy in i18n context because it filter on
        # root page's site SOURCE translation... not the current one!
        return self.descendant_of(site.root_page.localized)


class I18nQuerySet(I18nQuerySetMixin, QuerySet):
    pass


class I18nPageQuerySet(I18nQuerySetMixin, PageQuerySet):
    pass


class ImageManager(models.Manager):
    def get_queryset(self):
        return self._queryset_class(self.model).select_related("photographer")


class ImagePageManager(PageManager):
    def get_queryset(self):
        return (
            self._queryset_class(self.model)
            .select_related("image__photographer")
            .prefetch_related("image__renditions")
        )


I18nManager = models.Manager.from_queryset(I18nQuerySet)
I18nPageManager = PageManager.from_queryset(I18nPageQuerySet)
I18nIndexPageManager = ImagePageManager.from_queryset(I18nPageQuerySet)
