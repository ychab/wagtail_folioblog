from django.test import TestCase, modify_settings
from django.utils.cache import has_vary_header

from folioblog.blog.factories import BlogIndexPageFactory
from folioblog.user.factories import UserFactory


class PatchVaryMiddlewareTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(is_staff=True)
        cls.page = BlogIndexPageFactory()

    @modify_settings(MIDDLEWARE={
        'prepend': 'folioblog.core.middleware.PatchVaryMiddleware'
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
        'prepend': 'folioblog.core.middleware.PatchVaryMiddleware'
    })
    def test_vary_anonymous_wrong_method(self):
        response = self.client.post(self.page.url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(has_vary_header(response, 'Cookie'))

    @modify_settings(MIDDLEWARE={
        'prepend': 'folioblog.core.middleware.PatchVaryMiddleware'
    })
    def test_vary_authenticated_always_cache(self):
        self.client.force_login(self.user)
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(has_vary_header(response, 'Cookie'))

    def test_vary_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(has_vary_header(response, 'Cookie'))


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
