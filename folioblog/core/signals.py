from django.core.cache import cache

from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.images.models import AbstractImage
from wagtail.models import Page
from wagtail.snippets.models import get_snippet_models

from taggit.models import TagBase


def clear_cache_page(sender, **kwargs):
    # No matter which model instance is added/edit/deleted... clear ALL cache
    # to avoid cascading behavior! In that way, we could have a huge cache
    # duration if no changes are done for a looooong time!
    # Furthermore, changes are applied... immediatly!
    subclasses = tuple(
        [Page, TagBase, AbstractImage, BaseGenericSetting] + get_snippet_models()
    )
    if issubclass(sender, subclasses):
        cache.clear()
