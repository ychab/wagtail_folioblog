from folioblog.core.factories import BaseIndexPageFactory
from folioblog.search.models import SearchIndexPage


class SearchIndexPageFactory(BaseIndexPageFactory):
    class Meta:
        model = SearchIndexPage

    title = "Search"
    slug = "search"
