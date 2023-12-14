import logging

from django.db import connection
from django.middleware.cache import FetchFromCacheMiddleware, UpdateCacheMiddleware


class AnonymousUpdateCacheMiddleware(UpdateCacheMiddleware):
    def has_restriction(self, request, response):
        context_data = getattr(response, "context_data", None)
        page = (
            context_data["page"] if context_data and context_data.get("page") else None
        )

        # Prevent useless queries if we already know that it couldn't be cached.
        if page and self._should_update_cache(request, response):
            return bool(page.get_view_restrictions())

        return False

    def process_response(self, request, response):
        is_anonymous = not hasattr(request, "user") or request.user.is_anonymous
        has_restrictions = self.has_restriction(request, response)

        if is_anonymous and not has_restrictions:
            # Remove Vary (Cookie) added by SessionMiddleware
            # @see https://code.djangoproject.com/ticket/29971#comment:4
            # BTW, remove Vary Accept-Language too (rely on path).
            response.headers.pop("Vary", None)
            return super().process_response(request, response)

        return response


class AnonymousFetchCacheMiddleware(FetchFromCacheMiddleware):
    def process_request(self, request):
        if request.user.is_anonymous:
            return super().process_request(request)


class CountQueriesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("folioblog.profiling.middleware")

    def __call__(self, request):
        if request.path.startswith("/media"):
            return self.get_response(request)

        count_before = len(connection.queries)
        response = self.get_response(request)
        count_after = len(connection.queries)

        count = count_after - count_before
        self.logger.info(
            "SQL QUERIES on {} ==> {}".format(request.build_absolute_uri(), count)
        )

        return response
