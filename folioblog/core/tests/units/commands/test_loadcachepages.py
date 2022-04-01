from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from wagtail.images import get_image_model
from wagtail.models import Page, Site

import requests
import requests_mock
from wagtail_factories import CollectionFactory

from folioblog.blog.factories import (
    BlogCategoryFactory, BlogIndexPageFactory, BlogPageFactory,
)
from folioblog.core.factories import BasicPageFactory
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

        cls.site = Site.objects.get(is_default_site=True)
        cls.root_page_original = cls.site.root_page

        cls.folio_settings = FolioBlogSettings.load()
        cls.folio_settings.blog_pager_limit = 3
        cls.folio_settings.save()  # Save only after transaction is enabled

        cls.portfolio = PortfolioPageFactory(
            parent=None,
            services__0='service',
            skills__0='skill',
            cv_experiences__0='experience',
            team_members__0='member',
        )
        cls.site.root_page = cls.portfolio
        cls.site.save()

        # Then delete old homepage
        Page.objects.filter(pk=2).delete()

        root_collection = CollectionFactory(name='Gallery')
        for name in ['posts', 'videos']:
            CollectionFactory(name=name, parent=root_collection)

        cls.home_blog = HomePageFactory(parent=cls.portfolio)
        cls.gallery_page = GalleryPageFactory(parent=cls.portfolio)
        cls.index_posts = BlogIndexPageFactory(parent=cls.portfolio)
        cls.index_videos = VideoIndexPageFactory(parent=cls.portfolio)
        cls.index_search = SearchIndexPageFactory(parent=cls.portfolio)

        cls.basics = []
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, slug='disclaimer'))
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, slug='presentation'))
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, slug='cookies-policy'))
        cls.basics.append(BasicPageFactory(parent=cls.portfolio, slug='rgpd'))

        category = BlogCategoryFactory()
        cls.posts = []
        for i in range(0, cls.folio_settings.blog_pager_limit + 1):
            cls.posts.append(BlogPageFactory(parent=cls.index_posts, category=category))

        cls.videos = []
        for i in range(0, cls.folio_settings.video_pager_limit + 1):
            cls.videos.append(VideoPageFactory(parent=cls.index_videos))

        cls.pages = [
            cls.portfolio,
            cls.home_blog,
            cls.gallery_page,
            cls.index_posts,
            cls.index_videos,
            cls.index_search,
        ] + cls.basics + cls.posts + cls.videos

    @classmethod
    def tearDownClass(cls):
        # Because we change the site root page which is created by migrations,
        # it would affect next TestCases even if rollback is done because the
        # root page was done BEFORE entering into the SQL transaction.
        # As a result, we need to reset it manually.
        cls.site.root_page = cls.root_page_original
        cls.site.save(update_fields=['root_page'])
        super().tearDownClass()

    @requests_mock.Mocker()
    def test_load_all_pages(self, m):
        for page in self.pages:
            m.get(page.full_url, text='Ok')
        m.get(f'{self.site.root_url}/givemea404please', text='Ok')

        out = StringIO()
        call_command('loadcachepages', stdout=out)
        self.assertIn('All page cache loaded', out.getvalue())

        for page in self.pages:
            self.assertIn(f'Requesting: "{page.full_url}"', out.getvalue(), f'Page {page}({page.pk}) request check')

    @requests_mock.Mocker()
    def test_load_request_exception(self, m):
        for page in Page.objects.all():
            if page.slug == 'portfolio':
                m.get(page.full_url, exc=requests.exceptions.HTTPError)
            else:
                m.get(page.full_url, text='Ok')
        m.get(f'{self.site.root_url}/givemea404please', text='Ok')

        out = StringIO()
        call_command('loadcachepages', stdout=out)

        self.assertIn(f'Error on page {self.portfolio.full_url} with exc', out.getvalue())

    @requests_mock.Mocker()
    def test_load_request_error(self, m):
        for page in Page.objects.all():
            if page.slug == 'portfolio':
                m.get(page.full_url, status_code=400)
            else:
                m.get(page.full_url, text='Ok')
        m.get(f'{self.site.root_url}/givemea404please', text='Ok')

        out = StringIO()
        call_command('loadcachepages', stdout=out)

        self.assertIn(f'Error for page {self.portfolio.full_url} with status 400', out.getvalue())
