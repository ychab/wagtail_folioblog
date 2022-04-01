from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from folioblog.blog.models import BlogPage
from folioblog.core.models import FolioBlogSettings


@method_decorator(never_cache, name='dispatch')
class AutocompleteView(View):
    """
    To avoid cache flood by hacker... don't cache it too!
    """

    def get(self, request, query, *args, **kwargs):
        folio_settings = FolioBlogSettings.load(request_or_site=request)
        search_qs = BlogPage.objects.live().autocomplete(
            query=query,
            fields=['title'],
            operator=folio_settings.search_operator,
        )
        results = [{'title': str(p), 'href': p.url} for p in search_qs]
        return JsonResponse(results, safe=False)
