from django.conf import settings
from django.test import TestCase

from wagtail.models import Site

from wagtail_factories import SiteFactory

from folioblog.blog.factories import (
    BlogIndexPageFactory,
    BlogPageFactory,
    BlogPromoteFactory,
)
from folioblog.blog.models import BlogPage, BlogPromote
from folioblog.core.factories import LocaleFactory
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.home.factories import HomePageFactory
from folioblog.home.tests.units.htmlpages import HomeHTMLPage
from folioblog.video.factories import (
    VideoIndexPageFactory,
    VideoPageFactory,
    VideoPromoteFactory,
)
from folioblog.video.models import VideoPage, VideoPromote


class HomePageTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site.objects.get(is_default_site=True)
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.index_blog = BlogIndexPageFactory(parent=cls.site.root_page)
        cls.index_videos = VideoIndexPageFactory(parent=cls.site.root_page)
        cls.page = HomePageFactory(parent=cls.site.root_page)

    def tearDown(self):
        BlogPage.objects.all().delete()
        VideoPage.objects.all().delete()
        BlogPromote.objects.all().delete()
        VideoPromote.objects.all().delete()

    def test_list_none(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)

        self.assertIsNone(response.context["blog_snippet"])
        self.assertIsNone(response.context["video_snippet"])

    def test_list_live(self):
        BlogPageFactory(parent=self.index_blog, promoted=True, live=False)
        VideoPageFactory(parent=self.index_videos, promoted=True, live=False)

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["blog_snippet"].related_links.count(), 0)
        self.assertEqual(response.context["video_snippet"].related_links.count(), 0)

    def test_list_order(self):
        posts = []
        for i in range(0, 2):
            posts.append(BlogPageFactory(parent=self.index_blog, promoted=True))

        videos = []
        for i in range(0, 2):
            videos.append(VideoPageFactory(parent=self.index_videos, promoted=True))

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)

        blog_ids = (
            response.context["blog_snippet"]
            .related_links.order_by("sort_order")
            .values_list("related_page_id", flat=True)
        )
        self.assertListEqual(list(blog_ids), [p.pk for p in posts])

        video_ids = (
            response.context["video_snippet"]
            .related_links.order_by("sort_order")
            .values_list("related_page_id", flat=True)
        )
        self.assertListEqual(list(video_ids), [p.pk for p in videos])


class HomePageI18nPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)

        locale_fr = LocaleFactory(language_code="fr")
        locale_en = LocaleFactory(language_code="en")

        # Required links
        BlogIndexPageFactory(parent=site.root_page)
        VideoIndexPageFactory(parent=site.root_page)

        cls.page_fr = HomePageFactory(
            parent=site.root_page,
            locale=locale_fr,
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )

        blog_promote_fr = BlogPromoteFactory(locale=locale_fr)
        blog_promote_en = blog_promote_fr.copy_for_translation(locale_en)
        blog_promote_en.save()

        video_promote_fr = VideoPromoteFactory(locale=locale_fr)
        video_promote_en = video_promote_fr.copy_for_translation(locale_en)
        video_promote_en.save()

    def test_filter_language_fr(self):
        response = self.client.get(self.page_fr.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["blog_snippet"].locale.language_code, "fr")
        self.assertEqual(response.context["video_snippet"].locale.language_code, "fr")

    def test_filter_language_en(self):
        response = self.client.get(self.page_en.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["blog_snippet"].locale.language_code, "en")
        self.assertEqual(response.context["video_snippet"].locale.language_code, "en")


class HomePageMultiDomainTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePageFactory(slug="foo")
        home_other = HomePageFactory(slug="bar")

        cls.site = Site.objects.get(is_default_site=True)
        cls.site_other = SiteFactory(root_page=home_other)

        cls.blog_promote = BlogPromoteFactory(site=cls.site)
        BlogPromoteFactory(site=cls.site_other)

        cls.video_promote = VideoPromoteFactory(site=cls.site)
        VideoPromoteFactory(site=cls.site_other)

    def test_multi_site(self):
        response = self.client.get(self.home.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.blog_promote, response.context_data["blog_snippet"])
        self.assertEqual(self.video_promote, response.context_data["video_snippet"])


class HomeHTMLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page = HomePageFactory()
        # Just for links in template page...
        BlogIndexPageFactory()
        VideoIndexPageFactory()

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = HomeHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_title(), self.page.title)

    def test_masthead_content(self):
        masthead_txt = self.htmlpage.get_masterhead_content().replace("\n", "")
        self.assertIn(self.page.title, masthead_txt)
        self.assertIn(self.page.subheading, masthead_txt)

    def test_meta_og(self):
        meta = self.htmlpage.get_meta_og()
        rendition = self.page.image.get_rendition("fill-2400x1260|format-jpeg")
        self.assertEqual(meta["og:type"], "website")
        self.assertEqual(meta["og:site_name"], self.page.get_site().site_name)
        self.assertEqual(meta["og:locale"], self.page.locale.language_code)
        self.assertEqual(meta["og:title"], self.page.title)
        self.assertEqual(meta["og:url"], self.page.full_url)
        self.assertEqual(meta["og:description"], self.page.seo_description)
        self.assertEqual(meta["og:image"], rendition.full_url)
        self.assertEqual(meta["og:image:type"], mimetype(rendition.url))
        self.assertEqual(int(meta["og:image:width"]), rendition.width)
        self.assertEqual(int(meta["og:image:height"]), rendition.height)
        self.assertEqual(meta["og:image:alt"], self.page.caption)

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta["twitter:card"], "summary")

    def test_meta_canonical(self):
        href = self.htmlpage.get_canonical_href()
        self.assertEqual(href, self.page.full_url)


class HomeHTMLi18nTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_fr = HomePageFactory(
            locale=LocaleFactory(language_code="fr"),
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=LocaleFactory(language_code="en"),
            copy_parents=True,
            alias=True,
        )

    def test_lang_default(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = HomeHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), settings.LANGUAGE_CODE)

    def test_lang_fr(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = HomeHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_fr.locale.language_code)

    def test_lang_en(self):
        response = self.client.get(self.page_en.url)
        htmlpage = HomeHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_en.locale.language_code)

    def test_alternates(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = HomeHTMLPage(response)

        self.assertListEqual(
            sorted(htmlpage.get_meta_alternates()),
            sorted([page.full_url for page in [self.page_fr, self.page_en]]),
        )
