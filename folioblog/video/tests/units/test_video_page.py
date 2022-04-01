from html import unescape

from django.test import TestCase
from django.utils.formats import date_format
from django.utils.translation import gettext

from wagtail_factories import CollectionFactory

from folioblog.core.templatetags.folioblog import mimetype
from folioblog.video.factories import (
    VideoIndexPageFactory, VideoPageFactory, VideoTagFactory,
)
from folioblog.video.models import VideoPage
from folioblog.video.tests.units.htmlpages import VideoHTMLPage


class VideoPageTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.collection = CollectionFactory(name='Video thumbnail')
        cls.index = VideoIndexPageFactory()

    def tearDown(self):
        VideoPage.objects.all().delete()

    def test_page_status(self):
        page = VideoPageFactory(parent=self.index)
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)

    def test_page_tags(self):
        tag = VideoTagFactory(name='mysupertestingtag')
        page = VideoPageFactory(parent=self.index, tags=[tag])
        response = self.client.get(page.url)
        html = unescape(response.content.decode())
        self.assertIn(str(tag), html)

    def test_page_tags_random(self):
        page = VideoPageFactory(parent=self.index, tags__number=1)
        response = self.client.get(page.url)
        html = unescape(response.content.decode())
        self.assertIn(str(page.tags.first()), html)

    def test_related_pages(self):
        related_page = VideoPageFactory(parent=self.index)
        page = VideoPageFactory(parent=self.index, related_pages=[related_page])
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['related_links']), 1)
        self.assertEqual(response.context['related_links'][0].related_page.specific, related_page)

    def test_related_pages_multiple(self):
        page = VideoPageFactory(parent=self.index, related_pages__number=2)
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['related_links']), 2)


class VideoPageHTMLTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.index = VideoIndexPageFactory()
        cls.page = VideoPageFactory(parent=cls.index, tags__number=2)

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = VideoHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_title(), self.page.title)

    def test_masthead_content(self):
        masthead_txt = self.htmlpage.get_masterhead_content().replace('\n', '')

        page_tags = ' '.join([str(t) for t in self.page.tags.all()])
        page_date = '{} {}'.format(gettext('Posté le'), date_format(self.page.date, 'SHORT_DATE_FORMAT'))

        self.assertIn(str(self.page.category), masthead_txt)
        self.assertIn(self.page.title, masthead_txt)
        self.assertIn(self.page.subheading, masthead_txt)
        self.assertIn(page_tags, masthead_txt)
        self.assertIn(page_date, masthead_txt)

    def test_meta_og(self):
        meta = self.htmlpage.get_meta_og()
        embed = self.page.embed
        rendition = self.page.image.get_rendition('fill-2400x1260|format-jpeg')

        self.assertEqual(meta['og:type'], 'video.other')
        self.assertEqual(meta['og:site_name'], self.page.get_site().site_name)
        self.assertEqual(meta['og:locale'], self.page.locale.language_code)
        self.assertEqual(meta['og:title'], self.page.title)
        self.assertEqual(meta['og:url'], self.page.full_url)
        self.assertIn(meta['og:description'], self.page.seo_description)
        self.assertEqual(meta['og:image'], rendition.full_url)
        self.assertEqual(meta['og:image:type'], mimetype(rendition.url))
        self.assertEqual(int(meta['og:image:width']), rendition.width)
        self.assertEqual(int(meta['og:image:height']), rendition.height)
        self.assertEqual(meta['og:image:alt'], self.page.caption)

        self.assertEqual(meta['og:video'], embed.url)
        self.assertEqual(meta['og:video:type'], 'text/html')
        self.assertEqual(int(meta['og:video:width']), embed.width)
        self.assertEqual(int(meta['og:video:height']), embed.height)
        self.assertEqual(meta['video:release_date'], date_format(self.page.first_published_at, 'c'))
        self.assertListEqual(
            sorted(meta['video:tag']),
            sorted([str(self.page.category)] + [t.slug for t in self.page.tags.all()]),
        )

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        embed = self.page.embed
        self.assertEqual(meta['twitter:card'], 'player')
        self.assertEqual(meta['twitter:player'], embed.url)
        self.assertEqual(int(meta['twitter:player:width']), embed.width)
        self.assertEqual(int(meta['twitter:player:height']), embed.height)

    def test_social_links(self):
        elem = self.htmlpage.get_social_links()
        self.assertTrue(elem)

    def test_intro(self):
        intro = self.htmlpage.get_intro()
        self.assertEqual(self.page.intro, intro)

    def test_body(self):
        body = self.htmlpage.get_body()
        self.assertIn(self.page.body.replace('\n', ''), body.replace('\n', ''))
