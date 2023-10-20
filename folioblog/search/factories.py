from django.utils.translation import gettext_lazy as _

from folioblog.core.factories import BaseIndexPageFactory
from folioblog.search.models import SearchIndexPage


class SearchIndexPageFactory(BaseIndexPageFactory):
    class Meta:
        model = SearchIndexPage

    title = _("Recherche")
    slug = "search"
