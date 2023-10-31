from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from wagtail.models import Site

from wagtail_factories import SiteFactory

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.core.factories import FolioBlogSettingsFactory, LocaleFactory


class RssViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        # Create site settings if not exist yet
        FolioBlogSettingsFactory(site=cls.site)
        cls.site.refresh_from_db()

        # Then update settings.
        settings_factory = FolioBlogSettingsFactory.build(
            rss_feed__0__feeds__language="fr",
            rss_feed__0__feeds__title="Les derniers articles",
            rss_feed__1__feeds__language="en",
            rss_feed__1__feeds__title="The latest posts",
        )
        cls.site.folioblogsettings.rss_feed = settings_factory.rss_feed
        cls.site.folioblogsettings.save()

        cls.settings_fr = cls.site.folioblogsettings.rss_feed[0].value
        cls.settings_en = cls.site.folioblogsettings.rss_feed[1].value

        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)
        cls.pages_fr = []
        cls.pages_en = []

        for i in range(0, cls.settings_fr["limit"] + 1):
            page_fr = BlogPageFactory(parent=cls.index, locale=cls.locale_fr)
            page_en = page_fr.copy_for_translation(
                locale=cls.locale_en,
                copy_parents=True,
                alias=True,
            )
            cls.pages_fr.append(page_fr)
            cls.pages_en.append(page_en)

    def test_feed_fr(self):
        with translation.override("fr"):
            url = reverse("rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["feed_title"], self.settings_fr["title"])
        self.assertEqual(response.context["feed_title"], "Les derniers articles")
        self.assertEqual(
            response.context["feed_description"], self.settings_fr["description"]
        )
        self.assertLessEqual(
            len(response.context["feed_items"]), self.settings_fr["limit"]
        )

    def test_feed_en(self):
        with translation.override("en"):
            url = reverse("rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["feed_title"], self.settings_en["title"])
        self.assertEqual(response.context["feed_title"], "The latest posts")
        self.assertEqual(
            response.context["feed_description"], self.settings_en["description"]
        )
        self.assertLessEqual(
            len(response.context["feed_items"]), self.settings_en["limit"]
        )


class RssViewMissingSettingsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        # Create site settings if not exist yet
        FolioBlogSettingsFactory(site=cls.site, rss_feed=None)

        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        index = BlogIndexPageFactory(parent=cls.site.root_page)
        page_fr = BlogPageFactory(parent=index, locale=cls.locale_fr)
        page_fr.copy_for_translation(
            locale=cls.locale_en,
            copy_parents=True,
            alias=True,
        )

    def test_feed_fr(self):
        with translation.override("fr"):
            url = reverse("rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("feed_items"))

    def test_feed_en(self):
        with translation.override("en"):
            url = reverse("rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("feed_items"))


class RssViewMultiDomainTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        # Create site settings if not exist yet
        FolioBlogSettingsFactory(site=cls.site)
        cls.site.refresh_from_db()

        # Then update settings.
        settings_factory = FolioBlogSettingsFactory.build(
            rss_feed__0__feeds__language="fr",
            rss_feed__0__feeds__title="Les derniers articles",
            rss_feed__1__feeds__language="en",
            rss_feed__1__feeds__title="The latest posts",
        )
        cls.site.folioblogsettings.rss_feed = settings_factory.rss_feed
        cls.site.folioblogsettings.save()

        cls.settings_fr = cls.site.folioblogsettings.rss_feed[0].value
        cls.settings_en = cls.site.folioblogsettings.rss_feed[1].value

        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)
        cls.page_fr = BlogPageFactory(parent=cls.index, locale=cls.locale_fr)
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=cls.locale_en,
            copy_parents=True,
            alias=True,
        )

        site = SiteFactory()
        cls.other_index = BlogIndexPageFactory(parent=site.root_page)
        cls.other_page_fr = BlogPageFactory(
            parent=cls.other_index, locale=cls.locale_fr
        )
        cls.other_page_en = cls.other_page_fr.copy_for_translation(
            locale=cls.locale_en,
            copy_parents=True,
            alias=True,
        )

    def test_feed_fr(self):
        with translation.override("fr"):
            url = reverse("rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.index.get_translation(self.locale_fr), response.context["blog_index"]
        )
        self.assertEqual(len(response.context["feed_items"]), 1)
        self.assertEqual(self.page_fr.pk, response.context["feed_items"][0].pk)

        self.assertNotEqual(
            self.other_index.get_translation(self.locale_fr),
            response.context["blog_index"],
        )
        self.assertNotEqual(self.other_page_fr.pk, response.context["feed_items"][0].pk)

    def test_feed_en(self):
        with translation.override("en"):
            url = reverse("rss")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.index.get_translation(self.locale_en), response.context["blog_index"]
        )
        self.assertEqual(len(response.context["feed_items"]), 1)
        self.assertEqual(self.page_en.pk, response.context["feed_items"][0].pk)

        self.assertNotEqual(
            self.other_index.get_translation(self.locale_en),
            response.context["blog_index"],
        )
        self.assertNotEqual(self.other_page_en.pk, response.context["feed_items"][0].pk)
