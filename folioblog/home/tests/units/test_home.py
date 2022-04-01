from django.test import TestCase

from wagtail.models import Site

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.blog.models import BlogPage, BlogPromote
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.home.factories import HomePageFactory
from folioblog.home.tests.units.htmlpages import HomeHTMLPage
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory
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

        self.assertIsNone(response.context['blog_snippet'])
        self.assertIsNone(response.context['video_snippet'])

    def test_list_live(self):
        BlogPageFactory(parent=self.index_blog, promoted=True, live=False)
        VideoPageFactory(parent=self.index_videos, promoted=True, live=False)

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['blog_snippet'].related_links.count(), 0)
        self.assertEqual(response.context['video_snippet'].related_links.count(), 0)

    def test_list_order(self):
        posts = []
        for i in range(0, 2):
            posts.append(BlogPageFactory(parent=self.index_blog, promoted=True))

        videos = []
        for i in range(0, 2):
            videos.append(VideoPageFactory(parent=self.index_videos, promoted=True))

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)

        blog_ids = response.context['blog_snippet'].related_links \
            .order_by('sort_order') \
            .values_list('related_page_id', flat=True)
        self.assertListEqual(list(blog_ids), [p.pk for p in posts])

        video_ids = response.context['video_snippet'].related_links \
            .order_by('sort_order') \
            .values_list('related_page_id', flat=True)
        self.assertListEqual(list(video_ids), [p.pk for p in videos])


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
