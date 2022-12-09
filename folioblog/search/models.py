from django.db.models import Prefetch
from django.urls import reverse
from django.utils import translation
from django.utils.cache import add_never_cache_headers

from folioblog.blog.models import BlogCategory, BlogPage, BlogPageTag, BlogTag
from folioblog.core.models import BaseIndexPage, FolioBlogSettings
from folioblog.core.pagination import FolioBlogPaginator
from folioblog.search.form import SearchForm


class SearchIndexPage(BaseIndexPage):
    parent_page_types = ['portfolio.PortfolioPage']
    subpage_types = []

    def serve(self, request, *args, **kwargs):
        # Yes, of course we could cache it!
        # However, a hacker could easily flood it...!
        response = super().serve(request, *args, **kwargs)
        add_never_cache_headers(response)
        return response

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        folio_settings = FolioBlogSettings.load(request_or_site=request)
        page = request.GET.get('page', 1)  # pager link, not in form

        # Mimic FormView in WagtailPage to sanitize data
        form = SearchForm(data=request.GET)
        form.is_valid()
        if form.errors:
            context.update({'errors': form.errors})

        cleaned_data = form.cleaned_data
        has_filters = any([cleaned_data.get('query'), cleaned_data.get('categories'), cleaned_data.get('tags')])
        search_results = self.get_search_results(
            has_filters=has_filters,
            cleaned_data=cleaned_data,
            page=page,
            limit=folio_settings.search_limit,
            operator=folio_settings.search_operator,
        )
        search_counter = search_results.paginator.count if has_filters and hasattr(search_results, 'paginator') else None  # noqa

        context.update({
            'has_filters': has_filters,
            'form': form,
            'search_results': search_results,
            'search_counter': search_counter,
            'category_options': self.get_category_options(),
            'tag_options': self.get_tag_options(),
            'autocomplete_url': self.get_autocomplete_url(token='__QUERY__'),
        })
        return context

    def get_search_results(self, has_filters, cleaned_data, page, limit, operator='and'):
        search_results = BlogPage.objects.none()

        if has_filters:
            search_results = BlogPage.objects \
                .live() \
                .filter_locale(self.locale) \
                .select_related('category', 'image') \
                .prefetch_related(
                    'image__renditions',
                    Prefetch('tagged_items', BlogPageTag.objects.select_related('tag').all())
                ) \
                .order_by('-date')

            if cleaned_data.get('tags'):
                # Due to limitation of Wagtail search backend, filter it manually...
                # @see https://docs.wagtail.org/en/stable/topics/search/indexing.html#index-relatedfields
                tag_qs = search_results.filter(tags__in=cleaned_data['tags']).distinct()
                search_results = search_results.filter(pk__in=tag_qs)

            if cleaned_data.get('categories'):
                search_results = search_results.filter(category__in=cleaned_data['categories'])

            if cleaned_data.get('query'):
                search_results = search_results.search(cleaned_data['query'], operator=operator)

        # Pagination
        paginator = FolioBlogPaginator(search_results, limit)
        page_results = paginator.get_page(page)
        return page_results

    def get_tag_options(self):
        # No other choices than returning all tags for all languages...
        # Indeed, tag are unique by their slug and thus, make no sense to
        # translate them... @see TagBase.fields
        return [t['slug'] for t in BlogTag.objects
                .values('slug')
                .order_by('slug')
                .distinct()]

    def get_category_options(self):
        return BlogCategory.objects.filter_language().order_by('slug')

    def get_autocomplete_url(self, token):
        with translation.override(self.locale.language_code):
            return reverse('search-autocomplete', kwargs={'query': token})
