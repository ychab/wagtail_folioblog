from django.test import TestCase

from wagtail.models import Site

from folioblog.core.models import FolioBlogSettings
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.video.factories import (
    VideoCategoryFactory, VideoIndexPageFactory, VideoPageFactory,
)
from folioblog.video.models import VideoCategory, VideoPage
from folioblog.video.tests.units.htmlpages import VideoIndexHTMLPage


class VideoIndexPageTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.site = Site.objects.get(is_default_site=True)

        cls.folio_settings = FolioBlogSettings.load()
        cls.folio_settings.video_pager_limit = 3
        cls.folio_settings.save()

    @classmethod
    def setUpTestData(cls):
        cls.page = VideoIndexPageFactory()

    def tearDown(self):
        VideoPage.objects.all().delete()
        VideoCategory.objects.all().delete()

    def tests_categories_used(self):
        VideoPageFactory(parent=self.page, category__name='cinema')
        VideoPageFactory(parent=self.page, category__name='humour')
        VideoPageFactory(parent=self.page, category__name='humour')
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 2)

    def tests_categories_unsed(self):
        VideoCategoryFactory(name='foo')
        VideoCategoryFactory(name='bar')
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 0)

    def test_list_none(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['videos']), 0)

    def test_list_live(self):
        VideoPageFactory(parent=self.page, live=False)
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['videos']), 0)

    def test_list_not_child(self):
        VideoPageFactory(parent=self.site.root_page)
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['videos']), 0)

    def test_list_pagination(self):
        limit = self.folio_settings.video_pager_limit
        exceed = (limit * 2) + 1

        videos = []
        for i in range(0, exceed):
            videos.append(VideoPageFactory(parent=self.page, title=f'pager{i}'))
        videos.reverse()

        page = 2
        response = self.client.get(self.page.url, data={'page': page})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['videos']), limit)
        self.assertEqual(response.context['videos'].number, page)
        self.assertEqual(response.context['videos'][0].pk, videos[3].pk)
        self.assertEqual(response.context['videos'][1].pk, videos[4].pk)

    def test_list_pagination_invalid(self):
        limit = self.folio_settings.video_pager_limit
        exceed = (limit * 2) + 1

        for i in range(0, exceed):
            VideoPageFactory(parent=self.page, title=f'pager{i}')

        page = 50
        response = self.client.get(self.page.url, data={'page': page})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['videos']), 0)

    def test_list_order(self):
        videos = []
        for i in range(0, 3):
            videos.append(VideoPageFactory(parent=self.page))
        videos.reverse()

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['videos']), 3)

        self.assertEqual(response.context['videos'][0].pk, videos[0].pk)
        self.assertEqual(response.context['videos'][1].pk, videos[1].pk)
        self.assertEqual(response.context['videos'][2].pk, videos[2].pk)

    def test_list_filter_category(self):
        p1 = VideoPageFactory(parent=self.page, category__name='humour')
        VideoPageFactory(parent=self.page, category__name='cinema')

        response = self.client.get(self.page.url, data={'category': 'humour'})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['videos']), 1)
        self.assertEqual(response.context['videos'][0].pk, p1.pk)


class VideoIndexHTMLTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.page = VideoIndexPageFactory()

        cls.categories = [
            VideoCategoryFactory(name='Humour'),
            VideoCategoryFactory(name='Cinéma'),
            VideoCategoryFactory(name='Tutoriel'),
        ]
        VideoPageFactory(parent=cls.page, category=cls.categories[0])
        VideoPageFactory(parent=cls.page, category=cls.categories[1])

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = VideoIndexHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_title(), self.page.title)

    def test_masthead_content(self):
        masthead_txt = self.htmlpage.get_masterhead_content().replace('\n', '')
        self.assertIn(self.page.title, masthead_txt)
        self.assertIn(self.page.subheading, masthead_txt)

    def test_meta_og(self):
        meta = self.htmlpage.get_meta_og()
        rendition = self.page.image.get_rendition('fill-2400x1260|format-jpeg')
        self.assertEqual(meta['og:type'], 'website')
        self.assertEqual(meta['og:site_name'], self.page.get_site().site_name)
        self.assertEqual(meta['og:locale'], self.page.locale.language_code)
        self.assertEqual(meta['og:title'], self.page.title)
        self.assertEqual(meta['og:url'], self.page.full_url)
        self.assertEqual(meta['og:description'], self.page.seo_description)
        self.assertEqual(meta['og:image'], rendition.full_url)
        self.assertEqual(meta['og:image:type'], mimetype(rendition.url))
        self.assertEqual(int(meta['og:image:width']), rendition.width)
        self.assertEqual(int(meta['og:image:height']), rendition.height)
        self.assertEqual(meta['og:image:alt'], self.page.caption)

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta['twitter:card'], 'summary')

    def test_categories_used(self):
        filters = self.htmlpage.get_filter_categories()
        self.assertEqual(len(filters), 2)

        slugs = filters.keys()
        self.assertIn(self.categories[0].slug, slugs)
        self.assertIn(self.categories[1].slug, slugs)
