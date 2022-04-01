import logging

from django.db import connection


class PatchVaryMiddleware:
    """
    Ignore HTTP_COOKIE header for building cache key.
    Indeed, having cookies doesn't matter for public page (everyone should have
    the same.Well no in fact, they must!).

    For instance, AuthenticationMiddleware try to load user. To do so, it will
    try to access the session and if the session is accessed, the middleware
    SessionMiddleware will add a Vary Cookie header! So in other word, we have
    a Vary Cookie for every requests! Why?
    @see https://code.djangoproject.com/ticket/29971#comment:4

    As a consequence, cache key will be build with the content of ALL
    cookies. And unfortunetly with GA cookie, its value change for EVERY
    requests and thus, create a new entry cache every time because cache_key is
    never the same value...

    One approach could be to remove the GA cookie on server side. However, this
    is definitively NOT an elegant at all (I have tried, trust me!).

    An another approach is just to remove the Vary header... And hoping it won't
    broke some stuff!
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # For public page marked as cacheable, remove the Vary cookie header to
        # have a unique version of the cached page for everyone!
        if 'public' in response.get("Cache-Control", ()):
            response.headers.pop('Vary', None)

        return response


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
