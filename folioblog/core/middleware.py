import logging

from django.db import connection
from django.middleware.cache import (
    FetchFromCacheMiddleware, UpdateCacheMiddleware,
)


class AnonymousUpdateCacheMiddleware(UpdateCacheMiddleware):

    def process_response(self, request, response):
        # If we don't have the user, maybe we got a redirect or something else.
        if hasattr(request, 'user') and request.user.is_anonymous:
            # Remove Vary (Cookie) added by AuthenticationMiddleware
            # @see https://code.djangoproject.com/ticket/29971#comment:4
            response.headers.pop('Vary', None)
            return super().process_response(request, response)

        return response


class AnonymousFetchCacheMiddleware(FetchFromCacheMiddleware):

    def process_request(self, request):
        if request.user.is_anonymous:
            return super().process_request(request)


class CountQueriesMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('folioblog.profiling.middleware')

    def __call__(self, request):
        if request.path.startswith('/media'):
            return self.get_response(request)

        count_before = len(connection.queries)
        response = self.get_response(request)
        count_after = len(connection.queries)

        count = count_after - count_before
        self.logger.info('SQL QUERIES on {} ==> {}'.format(
            request.build_absolute_uri(), count))

        return response
