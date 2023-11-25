from django.test import TestCase
from django.urls import reverse

from wagtail.actions.copy_for_translation import CopyPageForTranslationAction
from wagtail.models import Page, Site

from bs4 import BeautifulSoup

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.core.factories import BasicPageFactory, LocaleFactory
from folioblog.core.utils.tests.units import SiteRootPageSwitchTestCase
from folioblog.portfolio.factories import PortfolioPageFactory
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory


class SitemapTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.portfolio = PortfolioPageFactory(parent=cls.site.root_page)

        # Once site root page is updated, create contents.
        cls.index_posts = BlogIndexPageFactory(parent=cls.portfolio)
        cls.index_videos = VideoIndexPageFactory(parent=cls.portfolio)

        cls.basic = BasicPageFactory(parent=cls.portfolio)
        cls.post = BlogPageFactory(parent=cls.index_posts)
        cls.video = VideoPageFactory(parent=cls.index_videos)

    def setUp(self):
        url = reverse("sitemap")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        xml_parsed = {}
        bs = BeautifulSoup(response.content, features="xml")
        urls = bs.find_all(name="url")
        for url in urls:
            loc = url.find(name="loc").text
            links = {
                l.attrs["hreflang"]: l.attrs["href"]
                for l in url.find_all(name="xhtml:link")  # noqa
            }
            xml_parsed[loc] = links

        self.xml_parsed = xml_parsed

    def test_sitemap_portfolio(self):
        url_default = self.portfolio.full_url
        self.assertIn(url_default, self.xml_parsed)
        hrefs = self.xml_parsed[url_default]
        self.assertFalse(hrefs)

    def test_sitemap_blog_index(self):
        url_default = self.index_posts.full_url
        self.assertIn(url_default, self.xml_parsed)
        hrefs = self.xml_parsed[url_default]
        self.assertFalse(hrefs)

    def test_sitemap_video_index(self):
        url_default = self.index_videos.full_url
        self.assertIn(url_default, self.xml_parsed)
        hrefs = self.xml_parsed[url_default]
        self.assertFalse(hrefs)

    def test_sitemap_basic_page(self):
        url_default = self.basic.full_url
        self.assertIn(url_default, self.xml_parsed)
        hrefs = self.xml_parsed[url_default]
        self.assertFalse(hrefs)

    def test_sitemap_blog_page(self):
        url_default = self.post.full_url
        self.assertIn(url_default, self.xml_parsed)
        hrefs = self.xml_parsed[url_default]
        self.assertFalse(hrefs)

    def test_sitemap_video_page(self):
        url_default = self.video.full_url
        self.assertIn(url_default, self.xml_parsed)
        hrefs = self.xml_parsed[url_default]
        self.assertFalse(hrefs)


class SitemapI18nTestCase(SiteRootPageSwitchTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        # Must inherit from root page in order to generate translations later.
        root_fr = Page.objects.get(slug="root", locale=cls.locale_fr)
        cls.portfolio_fr = PortfolioPageFactory(parent=root_fr, locale=cls.locale_fr)
        cls.root_page = cls.portfolio_fr
        super().setUpTestData()

        # Once site root page is updated, create contents.
        cls.index_posts_fr = BlogIndexPageFactory(
            parent=cls.portfolio_fr, locale=cls.locale_fr
        )
        cls.index_videos_fr = VideoIndexPageFactory(
            parent=cls.portfolio_fr, locale=cls.locale_fr
        )

        cls.basic_fr = BasicPageFactory(parent=cls.portfolio_fr, locale=cls.locale_fr)
        cls.post_fr = BlogPageFactory(parent=cls.index_posts_fr, locale=cls.locale_fr)
        cls.video_fr = VideoPageFactory(
            parent=cls.index_videos_fr, locale=cls.locale_fr
        )

        cls.portfolio_en = CopyPageForTranslationAction(
            page=cls.portfolio_fr,
            locale=cls.locale_en,
            alias=True,
            include_subtree=True,
        ).execute(skip_permission_checks=True)

    def setUp(self):
        url = reverse("sitemap")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        xml_parsed = {}
        bs = BeautifulSoup(response.content, "lxml")
        urls = bs.find_all(name="url")
        for url in urls:
            loc = url.find(name="loc").text
            links = {
                l.attrs["hreflang"]: l.attrs["href"]
                for l in url.find_all(name="xhtml:link")  # noqa
            }
            xml_parsed[loc] = links

        self.xml_parsed = xml_parsed

    def test_sitemap_portfolio_fr(self):
        url_fr = self.portfolio_fr.full_url
        url_en = self.portfolio_en.full_url

        self.assertIn(url_fr, self.xml_parsed)
        hrefs = self.xml_parsed[url_fr]
        self.assertIn("x-default", hrefs)
        self.assertIn("fr", hrefs)
        self.assertIn("en", hrefs)
        self.assertEqual(url_fr, hrefs["x-default"])
        self.assertEqual(url_fr, hrefs["fr"])
        self.assertEqual(url_en, hrefs["en"])

    def test_sitemap_portfolio_en(self):
        url_default = self.portfolio_fr.full_url
        url_fr = self.portfolio_fr.full_url
        url_en = self.portfolio_en.full_url

        self.assertIn(url_en, self.xml_parsed)
        hrefs = self.xml_parsed[url_en]
        self.assertIn("x-default", hrefs)
        self.assertIn("fr", hrefs)
        self.assertIn("en", hrefs)
        self.assertEqual(url_default, hrefs["x-default"])
        self.assertEqual(url_fr, hrefs["fr"])
        self.assertEqual(url_en, hrefs["en"])

    def test_sitemap_blog_index_fr(self):
        url_fr = self.portfolio_fr.full_url
        url_en = self.portfolio_en.full_url

        self.assertIn(url_fr, self.xml_parsed)
        hrefs = self.xml_parsed[url_fr]
        self.assertIn("x-default", hrefs)
        self.assertIn("fr", hrefs)
        self.assertIn("en", hrefs)
        self.assertEqual(url_fr, hrefs["x-default"])
        self.assertEqual(url_fr, hrefs["fr"])
        self.assertEqual(url_en, hrefs["en"])

    def test_sitemap_video_index_fr(self):
        url_fr = self.portfolio_fr.full_url
        url_en = self.portfolio_en.full_url

        self.assertIn(url_fr, self.xml_parsed)
        hrefs = self.xml_parsed[url_fr]
        self.assertIn("x-default", hrefs)
        self.assertIn("fr", hrefs)
        self.assertIn("en", hrefs)
        self.assertEqual(url_fr, hrefs["x-default"])
        self.assertEqual(url_fr, hrefs["fr"])
        self.assertEqual(url_en, hrefs["en"])

    def test_sitemap_basic_page_fr(self):
        url_fr = self.portfolio_fr.full_url
        url_en = self.portfolio_en.full_url

        self.assertIn(url_fr, self.xml_parsed)
        hrefs = self.xml_parsed[url_fr]
        self.assertIn("x-default", hrefs)
        self.assertIn("fr", hrefs)
        self.assertIn("en", hrefs)
        self.assertEqual(url_fr, hrefs["x-default"])
        self.assertEqual(url_fr, hrefs["fr"])
        self.assertEqual(url_en, hrefs["en"])

    def test_sitemap_blog_page_fr(self):
        url_fr = self.portfolio_fr.full_url
        url_en = self.portfolio_en.full_url

        self.assertIn(url_fr, self.xml_parsed)
        hrefs = self.xml_parsed[url_fr]
        self.assertIn("x-default", hrefs)
        self.assertIn("fr", hrefs)
        self.assertIn("en", hrefs)
        self.assertEqual(url_fr, hrefs["x-default"])
        self.assertEqual(url_fr, hrefs["fr"])
        self.assertEqual(url_en, hrefs["en"])

    def test_sitemap_video_page_fr(self):
        url_fr = self.portfolio_fr.full_url
        url_en = self.portfolio_en.full_url

        self.assertIn(url_fr, self.xml_parsed)
        hrefs = self.xml_parsed[url_fr]
        self.assertIn("x-default", hrefs)
        self.assertIn("fr", hrefs)
        self.assertIn("en", hrefs)
        self.assertEqual(url_fr, hrefs["x-default"])
        self.assertEqual(url_fr, hrefs["fr"])
        self.assertEqual(url_en, hrefs["en"])
