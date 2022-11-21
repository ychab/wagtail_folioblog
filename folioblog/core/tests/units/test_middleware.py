from django.core.cache import cache
from django.db import connection
from django.test import TestCase, modify_settings
from django.test.utils import CaptureQueriesContext
from django.utils.cache import has_vary_header

from folioblog.blog.factories import BlogIndexPageFactory
from folioblog.user.factories import UserFactory


class VaryAnonymousCacheMiddlewareTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(is_staff=True)
        cls.page = BlogIndexPageFactory()

    @modify_settings(MIDDLEWARE={
        'prepend': ['folioblog.core.middleware.AnonymousUpdateCacheMiddleware'],
        'append': ['folioblog.core.middleware.AnonymousFetchCacheMiddleware'],
    })
    def test_vary_anonymous_not(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(has_vary_header(response, 'Cookie'))

    def test_vary_anonymous(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(has_vary_header(response, 'Cookie'))

    @modify_settings(MIDDLEWARE={
        'prepend': ['folioblog.core.middleware.AnonymousUpdateCacheMiddleware'],
        'append': ['folioblog.core.middleware.AnonymousFetchCacheMiddleware'],
    })
    def test_vary_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(has_vary_header(response, 'Cookie'))

    def test_vary_authenticated_without_middleware(self):
        self.client.force_login(self.user)
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(has_vary_header(response, 'Cookie'))


@modify_settings(MIDDLEWARE={
    'prepend': ['folioblog.core.middleware.AnonymousUpdateCacheMiddleware'],
    'append': ['folioblog.core.middleware.AnonymousFetchCacheMiddleware'],
})
class AnonymousCacheMiddlewareTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(is_staff=True)
        cls.page = BlogIndexPageFactory()

    def tearDown(self):
        cache.clear()

    def test_anonymous(self):
        # No cache yet
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q['sql'] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

        # Cache hit
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q['sql'] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 0)
        self.assertIn('max-age=', response.headers.get('cache-control', ''))

    def test_authenticated(self):
        self.client.force_login(self.user)

        # No cache yet
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q['sql'] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

        # Still no cache
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q['sql'] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)
        self.assertNotIn('max-age=', response.headers.get('cache-control', ''))


@modify_settings(MIDDLEWARE={
    'prepend': 'folioblog.core.middleware.CountQueriesMiddleware'
})
class CountQueriesMiddlewareTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.page = BlogIndexPageFactory()

    def test_skip(self):
        rendition = self.page.image.get_rendition('original')
        with self.assertNoLogs('folioblog.profiling.middleware'):
            self.client.get(rendition.url)

    def test_count_queries(self):
        with self.assertLogs('folioblog.profiling.middleware') as cm:
            response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('SQL QUERIES on', cm.output[0])
