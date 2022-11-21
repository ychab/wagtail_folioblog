from django.test import TestCase
from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.utils.translation import gettext

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.blog.models import BlogPage
from folioblog.blog.tests.units.htmlpages import BlogPostHTMLPage
from folioblog.core.templatetags.folioblog import mimetype


class BlogPageTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory()

    def tearDown(self):
        BlogPage.objects.all().delete()

    def test_related_none(self):
        page = BlogPageFactory(parent=self.index)
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['related_links']), 0)

    def test_related_pages(self):
        related_page = BlogPageFactory(parent=self.index)
        page = BlogPageFactory(parent=self.index, related_pages=[related_page])
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['related_links']), 1)
        self.assertEqual(response.context['related_links'][0].related_page.specific, related_page)

    def test_related_pages_multiple(self):
        page = BlogPageFactory(parent=self.index, related_pages__number=2)
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['related_links']), 2)


class BlogPageHTMLTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory()
        cls.page = BlogPageFactory(
            parent=cls.index,
            tags__number=2,
            related_pages__number=1,
        )

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = BlogPostHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_status_code(), 200)
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
        rendition = self.page.image.get_rendition('fill-2400x1260|format-jpeg')
        self.assertEqual(meta['og:type'], 'article')
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

        self.assertEqual(meta['article:published_time'], date_format(localtime(self.page.first_published_at), 'c'))
        self.assertEqual(meta['article:modified_time'], date_format(localtime(self.page.last_published_at), 'c'))
        self.assertEqual(meta['article:section'], str(self.page.category))
        self.assertListEqual(
            sorted(meta['article:tag']),
            sorted([t.slug for t in self.page.tags.all()]),
        )

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta['twitter:card'], 'summary_large_image')

    def test_social_links(self):
        elem = self.htmlpage.get_social_links()
        self.assertTrue(elem)

    def test_intro(self):
        intro = self.htmlpage.get_intro()
        self.assertEqual(self.page.intro, intro)

    def test_body(self):
        body = self.htmlpage.get_body()
        self.assertIn(self.page.body.replace('\n', ''), body.replace('\n', ''))

    def test_blockquote(self):
        data = self.htmlpage.get_blockquote_with_caption()
        self.assertEqual(
            data['blockquote'].replace('\n', ''),
            self.page.blockquote.replace('\n', ''),
        )
        self.assertIn(self.page.blockquote_author, data['caption'])
        self.assertIn(self.page.blockquote_ref, data['caption'])

    def test_related_page(self):
        data = self.htmlpage.get_related_pages()
        page_related = self.page.related_links.first().related_page
        self.assertEqual(data[0]['title'], page_related.title)
        self.assertEqual(data[0]['url'], page_related.url)
