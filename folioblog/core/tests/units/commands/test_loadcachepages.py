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
from folioblog.gallery.factories import GalleryPageFactory
from folioblog.home.factories import HomePageFactory
from folioblog.portfolio.factories import PortfolioPageFactory
from folioblog.search.factories import SearchIndexPageFactory
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory

User = get_user_model()
Image = get_image_model()
Rendition = Image.get_rendition_model()


class LoadCachePagesCommandTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Due to PortfolioPage which doesn't seems to support deepcopy(), we
        cannot use setUpTestData(). However, we could still inject data (shared)
        between testmethods just after the SQL transaction begin!
        """
        super().setUpClass()
        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        root_collection = CollectionFactory(name="Gallery")

        cls.site = Site.objects.get(is_default_site=True)
        cls.root_page_original = cls.site.root_page

        cls.folio_settings = FolioBlogSettings.for_site(cls.site)
        cls.folio_settings.blog_pager_limit = 3
        cls.folio_settings.video_pager_limit = 3
        cls.folio_settings.gallery_collection = root_collection
        cls.folio_settings.save()  # Save only after transaction is enabled

        cls.portfolio = PortfolioPageFactory(
            parent=Page.objects.get(slug="root", locale=cls.locale_fr),
            locale=cls.locale_fr,
            services__0="service",
            # skills__0='skill',
            skills__0__skill__links__0__page=None,
            cv_experiences__0="experience",
            team_members__0="member",
        )
        cls.site.root_page = cls.portfolio
        cls.site.save()

        # Then delete old homepage
        Page.objects.filter(pk=2).delete()

        for name in ["posts", "videos"]:
            CollectionFactory(name=name, parent=root_collection)

        cls.home_blog = HomePageFactory(parent=cls.portfolio, locale=cls.locale_fr)
        cls.gallery_page = GalleryPageFactory(
            parent=cls.portfolio, locale=cls.locale_fr
        )
        cls.index_posts = BlogIndexPageFactory(
            parent=cls.portfolio, locale=cls.locale_fr
        )
        cls.index_videos = VideoIndexPageFactory(
            parent=cls.portfolio, locale=cls.locale_fr
        )
        cls.index_search = SearchIndexPageFactory(
            parent=cls.portfolio, locale=cls.locale_fr
        )

        cls.basics = []
        cls.basics.append(
            BasicPageFactory(
                parent=cls.portfolio, locale=cls.locale_fr, title="disclaimer"
            )
        )
        cls.basics.append(
            BasicPageFactory(
                parent=cls.portfolio, locale=cls.locale_fr, title="presentation"
            )
        )
        cls.basics.append(
            BasicPageFactory(
                parent=cls.portfolio, locale=cls.locale_fr, title="cookies-policy"
            )
        )
        cls.basics.append(
            BasicPageFactory(parent=cls.portfolio, locale=cls.locale_fr, title="rgpd")
        )

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

    @classmethod
    def tearDownClass(cls):
        # Because we change the site root page which is created by migrations,
        # it would affect next TestCases even if rollback is done because the
        # root page was done BEFORE entering into the SQL transaction.
        # As a result, we need to reset it manually.
        cls.site.root_page = cls.root_page_original
        cls.site.save(update_fields=["root_page"])
        super().tearDownClass()

    @requests_mock.Mocker()
    def test_load_all_pages(self, m):
        for page in self.pages:
            m.get(page.full_url, text="Ok")

        for lang in dict(settings.LANGUAGES).keys():
            for view_name in ["javascript-catalog", "rss"]:
                with translation.override(lang):
                    m.get(f"{self.site.root_url}{reverse(view_name)}", text="Ok")

        m.get(f"{self.site.root_url}/givemea404please", text="Ok")

        out = StringIO()
        call_command("loadcachepages", stdout=out)
        self.assertIn("All page cache loaded", out.getvalue())

        for page in self.pages:
            self.assertIn(
                f'Requesting: "{page.full_url}"',
                out.getvalue(),
                f"Page {page}({page.pk}) request check",
            )

    @requests_mock.Mocker()
    def test_load_request_exception(self, m):
        url_exc = None

        for page in Page.objects.all():
            # Special handling for exception
            if page.slug == "portfolio":
                url_exc = page.full_url
                m.get(url_exc, exc=requests.exceptions.HTTPError)
            else:
                m.get(page.full_url, text="Ok")

        for lang in dict(settings.LANGUAGES).keys():
            for view_name in ["javascript-catalog", "rss"]:
                with translation.override(lang):
                    m.get(f"{self.site.root_url}{reverse(view_name)}", text="Ok")

        m.get(f"{self.site.root_url}/givemea404please", text="Ok")

        out = StringIO()
        call_command("loadcachepages", stdout=out)

        self.assertIn(f"Error on page {url_exc} with exc", out.getvalue())

    @requests_mock.Mocker()
    def test_load_request_error(self, m):
        url_error = None

        for page in Page.objects.all():
            if page.slug == "portfolio":
                url_error = page.full_url
                m.get(url_error, status_code=400)
            else:
                m.get(page.full_url, text="Ok")

        for lang in dict(settings.LANGUAGES).keys():
            for view_name in ["javascript-catalog", "rss"]:
                with translation.override(lang):
                    m.get(f"{self.site.root_url}{reverse(view_name)}", text="Ok")

        m.get(f"{self.site.root_url}/givemea404please", text="Ok")

        out = StringIO()
        call_command("loadcachepages", stdout=out)

        self.assertIn(f"Error for page {url_error} with status 400", out.getvalue())


class LoadCachePagesMultiDomainCommandTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        # Website A
        cls.home = HomePageFactory(locale=cls.locale_fr, slug="home")
        cls.site = SiteFactory(root_page=cls.home)
        FolioBlogSettingsFactory(site=cls.site)
        cls.index = BlogIndexPageFactory(parent=cls.home, locale=cls.locale_fr)
        cls.post = BlogPageFactory(parent=cls.index, locale=cls.locale_fr)

        # Website B
        cls.other_home = HomePageFactory(locale=cls.locale_fr, slug="home_other")
        cls.other_site = SiteFactory(root_page=cls.other_home)
        FolioBlogSettingsFactory(site=cls.other_site)
        cls.other_index = BlogIndexPageFactory(
            parent=cls.other_home, locale=cls.locale_fr
        )
        cls.other_post = BlogPageFactory(parent=cls.other_index, locale=cls.locale_fr)

        cls.pages = [
            cls.home,
            cls.index,
            cls.post,
            cls.other_home,
            cls.other_index,
            cls.other_post,
        ]

    @requests_mock.Mocker()
    def setUp(self, m):
        for page in Page.objects.all():
            m.get(page.full_url, text="Ok")

        for site in Site.objects.all():
            for locale in [self.locale_fr, self.locale_en]:
                for view_name in ["javascript-catalog", "rss"]:
                    with translation.override(locale.language_code):
                        m.get(f"{site.root_url}{reverse(view_name)}", text="Ok")

            m.get(f"{site.root_url}/givemea404please", text="Ok")

    def test_multi_domains(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)
        self.assertIn(f"About requesting pages of site {self.site}:", out.getvalue())
        self.assertIn(
            f"About requesting pages of site {self.other_site}:", out.getvalue()
        )

        for page in self.pages:
            self.assertIn(
                f'Requesting: "{page.full_url}"',
                out.getvalue(),
                f"Page {page}({page.pk}) request check",
            )


class LoadCachePagesCollectionRootNoneCommandTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.locale_fr = LocaleFactory(language_code="fr")
        cls.locale_en = LocaleFactory(language_code="en")

        cls.home = HomePageFactory(locale=cls.locale_fr, slug="home")
        cls.site = SiteFactory(root_page=cls.home)
        FolioBlogSettingsFactory(site=cls.site, gallery_collection=None)

        cls.collection = CollectionFactory()
        cls.image = ImageFactory(collection=cls.collection)

        cls.index = BlogIndexPageFactory(parent=cls.home, locale=cls.locale_fr)
        cls.post = BlogPageFactory(
            parent=cls.index, locale=cls.locale_fr, image=cls.image
        )
        cls.gallery = GalleryPageFactory(parent=cls.home, locale=cls.locale_fr)

        cls.pages = [
            cls.home,
            cls.index,
            cls.post,
        ]

    @requests_mock.Mocker()
    def setUp(self, m):
        for page in Page.objects.all():
            m.get(page.full_url, text="Ok")

        for site in Site.objects.all():
            for locale in [self.locale_fr, self.locale_en]:
                for view_name in ["javascript-catalog", "rss"]:
                    with translation.override(locale.language_code):
                        m.get(f"{site.root_url}{reverse(view_name)}", text="Ok")

            m.get(f"{site.root_url}/givemea404please", text="Ok")

    def test_collection_without_settings(self):
        out = StringIO()
        call_command("loadcachepages", stdout=out)

        self.assertIn(
            f'Requesting: "{self.gallery.full_url}?ajax=1&collection={self.collection.pk}"',
            out.getvalue(),
        )
