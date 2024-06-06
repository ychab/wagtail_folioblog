from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from wagtail.actions.copy_for_translation import CopyPageForTranslationAction
from wagtail.images import get_image_model
from wagtail.models import Page, Site

import requests
import requests_mock
from wagtail_factories import CollectionFactory, SiteFactory

from folioblog.blog.factories import (
    BlogCategoryFactory,
    BlogIndexPageFactory,
    BlogPageFactory,
)
from folioblog.core.factories import (
    BasicPageFactory,
    FolioBlogSettingsFactory,
    ImageFactory,
    LocaleFactory,
)
from folioblog.core.models import FolioBlogSettings
from folioblog.core.utils.tests.units import SiteRootPageSwitchTestCase
from folioblog.gallery.factories import GalleryPageFactory
from folioblog.home.factories import HomePageFactory
from folioblog.portfolio.factories import PortfolioPageFactory
from folioblog.search.factories import SearchIndexPageFactory
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory

User = get_user_model()
Image = get_image_model()
Rendition = Image.get_rendition_model()


class LoadCachePagesCommandTestCase(SiteRootPageSwitchTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        root_collection = CollectionFactory(name="Gallery")

        cls.site = Site.objects.get(is_default_site=True)

        cls.folio_settings = FolioBlogSettings.for_site(cls.site)
        cls.folio_settings.blog_pager_limit = 3
        cls.folio_settings.video_pager_limit = 3
        cls.folio_settings.gallery_collection = root_collection
        cls.folio_settings.save()

        # Must inherit from root page in order to generate translations later.
        cls.portfolio = PortfolioPageFactory(
            parent=Page.objects.get(slug="root", locale=cls.locale_fr),
            locale=cls.locale_fr,
            services__0="service",
            skills__0__skill__links__0__page=None,
            cv_experiences__0="experience",
            team_members__0="member",
        )
        cls.root_page = cls.portfolio
        super().setUpTestData()

        for name in ["posts", "videos"]:
            CollectionFactory(name=name, parent=root_collection)

        cls.home_blog = HomePageFactory(parent=cls.portfolio, locale=cls.locale_fr)
        cls.gallery_page = GalleryPageFactory(parent=cls.portfolio, locale=cls.locale_fr)
        cls.index_posts = BlogIndexPageFactory(parent=cls.portfolio, locale=cls.locale_fr)
        cls.index_videos = VideoIndexPageFactory(parent=cls.portfolio, locale=cls.locale_fr)
        cls.index_search = SearchIndexPageFactory(parent=cls.portfolio, locale=cls.locale_fr)

        cls.basics = []
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, locale=cls.locale_fr, title="disclaimer"))
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, locale=cls.locale_fr, title="presentation"))
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, locale=cls.locale_fr, title="cookies-policy"))
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, locale=cls.locale_fr, title="rgpd"))

        category = BlogCategoryFactory(locale=cls.locale_fr)
        cls.posts = []
        for i in range(0, cls.folio_settings.blog_pager_limit + 1):
            cls.posts.append(
                BlogPageFactory(
                    parent=cls.index_posts,
                    locale=cls.locale_fr,
                    category=category,
                )
            )

        cls.videos = []
        for i in range(0, cls.folio_settings.video_pager_limit + 1):
            cls.videos.append(
                VideoPageFactory(
                    parent=cls.index_videos,
                    locale=cls.locale_fr,
                )
            )

        cls.portfolio_en = CopyPageForTranslationAction(
            page=cls.portfolio,
            locale=cls.locale_en,
            alias=True,
            include_subtree=False,
        ).execute(skip_permission_checks=True)

        cls.pages = (
            [
                cls.portfolio,
                cls.portfolio_en,
                cls.home_blog,
                cls.gallery_page,
                cls.index_posts,
                cls.index_videos,
                cls.index_search,
            ]
            + cls.basics
            + cls.posts
            + cls.videos
        )

    def setUp(self):
        self.mock_request = requests_mock.Mocker()
        self.mock_request.start()

        for page in self.pages:
            self.mock_request.get(page.full_url, text="Ok")

        for site in Site.objects.all():
            for view_name in ["javascript-catalog", "rss"]:
                for lang in dict(settings.LANGUAGES).keys():
                    with translation.override(lang):
                        url = reverse(view_name)
                    self.mock_request.get(f"{site.root_url}{url}", text="Ok")

            self.mock_request.get(f"{site.root_url}/givemea404please", status_code=404)

    def tearDown(self):
        self.mock_request.stop()

    def test_load_all_pages(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)
        self.assertIn("All page cache loaded", out.getvalue())

        for page in self.pages:
            self.assertIn(
                f'Requesting: GET "{page.full_url}"',
                out.getvalue(),
                f"Page {page}({page.pk}) request check",
            )

    def test_load_request_exception(self):
        self.mock_request.get(self.portfolio.full_url, exc=requests.exceptions.HTTPError)

        out = StringIO()
        call_command("loadcachepages", stdout=out)
        self.assertIn(f"Error on page {self.portfolio.full_url} with exc", out.getvalue())

    def test_load_request_error(self):
        self.mock_request.get(self.portfolio.full_url, status_code=400)

        out = StringIO()
        call_command("loadcachepages", stdout=out)
        self.assertIn(f"Error for page {self.portfolio.full_url} with status 400", out.getvalue())


class LoadCachePagesMultiDomainCommandTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Website A
        cls.site = Site.objects.get(is_default_site=True)
        cls.home = HomePageFactory(parent=cls.site.root_page)
        FolioBlogSettingsFactory(site=cls.site)
        cls.blog_index = BlogIndexPageFactory(parent=cls.home)
        cls.post = BlogPageFactory(parent=cls.blog_index, category__slug="foo")
        cls.video_index = VideoIndexPageFactory(parent=cls.home)
        cls.video = VideoPageFactory(parent=cls.video_index, category__slug="foo")

        # Website B
        cls.other_home = HomePageFactory(parent=None)
        cls.other_site = SiteFactory(root_page=cls.other_home)
        FolioBlogSettingsFactory(site=cls.other_site)
        cls.other_blog_index = BlogIndexPageFactory(parent=cls.other_home)
        cls.other_post = BlogPageFactory(parent=cls.other_blog_index, category__slug="bar")
        cls.other_video_index = VideoIndexPageFactory(parent=cls.other_home)
        cls.other_video = VideoPageFactory(parent=cls.other_video_index, category__slug="bar")

        cls.pages = [
            cls.home.get_parent(),
            cls.home,
            cls.blog_index,
            cls.post,
            cls.video_index,
            cls.video,
            # Other site
            cls.other_home,
            cls.other_blog_index,
            cls.other_post,
            cls.other_video_index,
            cls.other_video,
        ]

    def setUp(self):
        self.mock_request = requests_mock.Mocker()
        self.mock_request.start()

        for page in self.pages:
            self.mock_request.get(page.full_url, text="Ok")

        for site in Site.objects.all():
            for view_name in ["javascript-catalog", "rss"]:
                for lang in dict(settings.LANGUAGES).keys():
                    with translation.override(lang):
                        url = reverse(view_name)
                    self.mock_request.get(f"{site.root_url}{url}", text="Ok")

            self.mock_request.get(f"{site.root_url}/givemea404please", status_code=404)

    def tearDown(self):
        self.mock_request.stop()

    def test_multi_domains(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)
        self.assertIn(f"About requesting pages of site {self.site}:", out.getvalue())
        self.assertIn(f"About requesting pages of site {self.other_site}:", out.getvalue())

        for page in self.pages:
            self.assertIn(
                f'Requesting: GET "{page.full_url}"',
                out.getvalue(),
                f"Page {page}({page.pk}) request check",
            )

    def test_blog_categories_filter(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)

        self.assertIn(
            f"{self.blog_index.full_url}?ajax=1&page=1&category={self.post.category.slug}",
            out.getvalue(),
        )
        self.assertNotIn(
            f"{self.blog_index.full_url}?ajax=1&page=1&category={self.other_post.category.slug}",
            out.getvalue(),
        )

        self.assertIn(
            f"{self.other_blog_index.full_url}?ajax=1&page=1&category={self.other_post.category.slug}",
            out.getvalue(),
        )
        self.assertNotIn(
            f"{self.other_blog_index.full_url}?ajax=1&page=1&category={self.post.category.slug}",
            out.getvalue(),
        )

    def test_video_categories_filter(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)

        self.assertIn(
            f"{self.video_index.full_url}?ajax=1&page=1&category={self.video.category.slug}",
            out.getvalue(),
        )
        self.assertNotIn(
            f"{self.video_index.full_url}?ajax=1&page=1&category={self.other_video.category.slug}",
            out.getvalue(),
        )

        self.assertIn(
            f"{self.other_video_index.full_url}?ajax=1&page=1&category={self.other_video.category.slug}",
            out.getvalue(),
        )
        self.assertNotIn(
            f"{self.other_video_index.full_url}?ajax=1&page=1&category={self.video.category.slug}",
            out.getvalue(),
        )


class LoadCachePagesCollectionRootNoneCommandTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.home = HomePageFactory(parent=cls.site.root_page)
        FolioBlogSettingsFactory(site=cls.site, gallery_collection=None)

        cls.collection = CollectionFactory()
        cls.image = ImageFactory(collection=cls.collection)

        cls.index = BlogIndexPageFactory(parent=cls.home)
        cls.post = BlogPageFactory(parent=cls.index, image=cls.image)
        cls.gallery = GalleryPageFactory(parent=cls.home)

        cls.pages = [
            cls.home.get_parent(),
            cls.home,
            cls.index,
            cls.post,
            cls.gallery,
        ]

    def setUp(self):
        self.mock_request = requests_mock.Mocker()
        self.mock_request.start()

        for page in self.pages:
            self.mock_request.get(page.full_url, text="Ok")

        for site in Site.objects.all():
            for view_name in ["javascript-catalog", "rss"]:
                for lang in dict(settings.LANGUAGES).keys():
                    with translation.override(lang):
                        url = reverse(view_name)
                    self.mock_request.get(f"{site.root_url}{url}", text="Ok")

            self.mock_request.get(f"{site.root_url}/givemea404please", status_code=404)

    def tearDown(self):
        self.mock_request.stop()

    def test_collection_without_settings(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)

        self.assertIn(
            f'Requesting: GET "{self.gallery.full_url}?ajax=1&collection={self.collection.pk}"',
            out.getvalue(),
        )


class LoadCachePagesPrivateCommandTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        FolioBlogSettingsFactory(site=cls.site)

        cls.home = HomePageFactory(parent=cls.site.root_page)
        cls.index = BlogIndexPageFactory(parent=cls.home, is_private=True)
        cls.post = BlogPageFactory(parent=cls.index)

        cls.pages = [
            cls.home.get_parent(),
            cls.home,
            cls.index,
            cls.post,
        ]

    def setUp(self):
        self.mock_request = requests_mock.Mocker()
        self.mock_request.start()

        for page in self.pages:
            self.mock_request.get(page.full_url, text="Ok")

        for site in Site.objects.all():
            for view_name in ["javascript-catalog", "rss"]:
                for lang in dict(settings.LANGUAGES).keys():
                    with translation.override(lang):
                        url = reverse(view_name)
                    self.mock_request.get(f"{site.root_url}{url}", text="Ok")

            self.mock_request.get(f"{site.root_url}/givemea404please", status_code=404)

    def tearDown(self):
        self.mock_request.stop()

    def test_private_page_not_fetched(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)
        self.assertIn(
            f'Requesting: GET "{self.home.full_url}"',
            out.getvalue(),
        )
        self.assertNotIn(
            f'Requesting: GET "{self.index.full_url}"',
            out.getvalue(),
        )
        self.assertNotIn(
            f'Requesting: GET "{self.post.full_url}"',
            out.getvalue(),
        )
