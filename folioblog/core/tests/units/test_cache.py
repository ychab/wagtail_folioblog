from django.core.cache import cache
from django.db import connection
from django.test import TestCase, modify_settings
from django.test.utils import CaptureQueriesContext

from folioblog.blog.factories import (
    BlogCategoryFactory,
    BlogIndexPageFactory,
    BlogPageFactory,
    BlogTagFactory,
)
from folioblog.core.apps import connect_cache_signal
from folioblog.core.factories import ImageFactory


@modify_settings(
    MIDDLEWARE={
        "prepend": ["folioblog.core.middleware.AnonymousUpdateCacheMiddleware"],
        "append": ["folioblog.core.middleware.AnonymousFetchCacheMiddleware"],
    }
)
class ResetCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory()
        cls.category = BlogCategoryFactory()
        cls.tag = BlogTagFactory()
        cls.image = ImageFactory()

        cls.page = BlogPageFactory(
            parent=cls.index,
            category=cls.category,
            image=cls.image,
            tags=[cls.tag],
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        connect_cache_signal()

    def tearDown(self):
        cache.clear()

    def test_cache_page(self):
        # Not cached yet
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

        # Cache hit
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 0)

    def test_cache_clear_page(self):
        # No cache yet
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

        # Cache hit
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 0)

        self.page.save()

        # No cache (rebuild)
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

    def test_cache_clear_snippet(self):
        # No cache yet
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

        # Cache hit
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 0)

        self.category.save()

        # No cache (rebuild)
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

    def test_cache_clear_tag(self):
        # No cache yet
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

        # Cache hit
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 0)

        self.tag.save()

        # No cache (rebuild)
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

    def test_cache_clear_image(self):
        # No cache yet
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)

        # Cache hit
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 0)

        self.image.save()

        # No cache (rebuild)
        with CaptureQueriesContext(connection) as cm:
            response = self.client.get(self.page.url)
        count = len([q["sql"] for q in cm.captured_queries])
        self.assertEqual(response.status_code, 200)
        self.assertGreater(count, 0)
