from django.test import TestCase
from django.urls import reverse

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.core.models import FolioBlogSettings


class RssViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.folio_settings = FolioBlogSettings.load()
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory()

        cls.posts = []
        for i in range(0, cls.folio_settings.rss_limit + 1):
            cls.posts.append(BlogPageFactory(parent=cls.index))

    def test_feed(self):
        response = self.client.get(reverse('rss'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['feed_title'], self.folio_settings.rss_title)
        self.assertEqual(response.context['feed_description'], self.folio_settings.rss_description)
        self.assertEqual(len(response.context['feed_items']), self.folio_settings.rss_limit)
