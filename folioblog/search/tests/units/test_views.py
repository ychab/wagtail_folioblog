from django.test import TestCase
from django.urls import reverse

from wagtail.models import Site

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.blog.models import BlogPage
from folioblog.core.models import FolioBlogSettings


class AutocompleteViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.folio_settings = FolioBlogSettings.load()
        cls.folio_settings.search_operator = 'or'
        cls.folio_settings.save()

        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)

    def tearDown(self):
        BlogPage.objects.all().delete()

    def test_none(self):
        url = reverse('search-autocomplete', kwargs={'query': 'foo'})
        response = self.client.get(url, content_type='application/json')
        json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json)

    def test_match_single(self):
        p = BlogPageFactory(parent=self.index, title='foobar')
        BlogPageFactory(parent=self.index, title='baz')

        url = reverse('search-autocomplete', kwargs={'query': 'foo'})
        response = self.client.get(url, content_type='application/json')
        json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['title'], p.title)
        self.assertEqual(json[0]['href'], p.url)

    def test_match_multiple(self):
        p1 = BlogPageFactory(parent=self.index, title='foobar')
        p2 = BlogPageFactory(parent=self.index, title='foozoo')

        url = reverse('search-autocomplete', kwargs={'query': 'foo'})
        response = self.client.get(url, content_type='application/json')
        json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 2)
        self.assertListEqual(
            sorted([p['title'] for p in json]),
            sorted([p1.title, p2.title]),
        )
