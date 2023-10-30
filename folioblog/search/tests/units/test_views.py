from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from wagtail.models import Site

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.blog.models import BlogPage
from folioblog.core.factories import LocaleFactory
from folioblog.core.models import FolioBlogSettings


class AutocompleteViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.folio_settings = FolioBlogSettings.for_site(cls.site)
        cls.folio_settings.search_operator = "or"
        cls.folio_settings.save()

        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)

    def tearDown(self):
        BlogPage.objects.all().delete()

    def test_none(self):
        url = reverse("search-autocomplete", kwargs={"query": "foo"})
        response = self.client.get(url, content_type="application/json")
        json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json)

    def test_match_single(self):
        p = BlogPageFactory(parent=self.index, title="foobar")
        BlogPageFactory(parent=self.index, title="baz")

        url = reverse("search-autocomplete", kwargs={"query": "foo"})
        response = self.client.get(url, content_type="application/json")
        json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]["title"], p.title)
        self.assertEqual(json[0]["href"], p.url)

    def test_match_multiple(self):
        p1 = BlogPageFactory(parent=self.index, title="foobar")
        p2 = BlogPageFactory(parent=self.index, title="foozoo")

        url = reverse("search-autocomplete", kwargs={"query": "foo"})
        response = self.client.get(url, content_type="application/json")
        json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 2)
        self.assertListEqual(
            sorted([p["title"] for p in json]),
            sorted([p1.title, p2.title]),
        )


class AutocompleteI18nViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        locale_fr = LocaleFactory(language_code="fr")
        locale_en = LocaleFactory(language_code="en")

        site = Site.objects.get(is_default_site=True)
        cls.index_fr = BlogIndexPageFactory(
            parent=site.root_page,
            locale=locale_fr,
        )

        for i in range(0, 3):
            post_fr = BlogPageFactory(
                parent=cls.index_fr,
                locale=locale_fr,
                title=f"titre_{i}",
            )
            if i == 0:
                post_en = post_fr.copy_for_translation(
                    locale=locale_en,
                    copy_parents=True,
                    alias=True,
                )
                post_en.title = "title"
                post_en.slug = "title"
                post_en.save()

    def test_autocomplete_fr(self):
        with translation.override("fr"):
            url = reverse("search-autocomplete", kwargs={"query": "titre"})

        response = self.client.get(url, content_type="application/json")
        json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 3)
        self.assertNotIn("/fr/", json[0]["href"])
        self.assertNotIn("/fr/", json[1]["href"])
        self.assertNotIn("/fr/", json[2]["href"])

    def test_autocomplete_en(self):
        with translation.override("en"):
            url = reverse("search-autocomplete", kwargs={"query": "title"})

        response = self.client.get(url, content_type="application/json")
        json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json), 1)
        self.assertIn("/en/", json[0]["href"])
