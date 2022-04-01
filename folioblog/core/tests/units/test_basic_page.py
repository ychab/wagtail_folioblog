from django.test import TestCase

from wagtail.models import Site

from folioblog.core.factories import BasicPageFactory
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.core.tests.units.htmlpages import BasicHTMLPage


class BasicPageTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.page = BasicPageFactory(parent=cls.site.root_page)

    def test_page_status(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)

    def test_related_pages(self):
        related_page = BasicPageFactory(parent=self.site.root_page)
        page = BasicPageFactory(parent=self.site.root_page, related_pages=[related_page])
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['related_links']), 1)
        self.assertEqual(response.context['related_links'][0].related_page.specific, related_page)

    def test_related_pages_multiple(self):
        page = BasicPageFactory(parent=self.site.root_page, related_pages__number=2)
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['related_links']), 2)


class BasicPageHTMLTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.page = BasicPageFactory(parent=site.root_page)

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = BasicHTMLPage(response)

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
        self.assertIn(meta['og:description'], self.page.seo_description)
        self.assertEqual(meta['og:image'], rendition.full_url)
        self.assertEqual(meta['og:image:type'], mimetype(rendition.url))
        self.assertEqual(int(meta['og:image:width']), rendition.width)
        self.assertEqual(int(meta['og:image:height']), rendition.height)
        self.assertEqual(meta['og:image:alt'], self.page.caption)

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta['twitter:card'], 'summary')

    def test_intro(self):
        intro = self.htmlpage.get_intro()
        self.assertEqual(self.page.intro, intro)

    def test_body(self):
        body = self.htmlpage.get_body()
        self.assertIn(self.page.body.replace('\n', ''), body.replace('\n', ''))
