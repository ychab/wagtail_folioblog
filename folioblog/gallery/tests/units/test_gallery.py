from django.test import TestCase

from wagtail.images import get_image_model

from wagtail_factories import CollectionFactory

from folioblog.blog.factories import BlogPageFactory
from folioblog.blog.models import BlogPage
from folioblog.core.factories import BasicPageFactory, ImageFactory
from folioblog.core.models import BasicPage
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.gallery.factories import GalleryPageFactory
from folioblog.gallery.tests.units.htmlpages import GalleryHTMLPage

Image = get_image_model()


class GalleryPageTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        root_collection = CollectionFactory(name='Gallery')

        cls.collections = {}
        for name in ['page', 'post', 'video']:
            collection = CollectionFactory(name=name, parent=root_collection)
            cls.collections[name] = collection

        cls.page = GalleryPageFactory()

    def tearDown(self):
        BlogPage.objects.all().delete()
        BasicPage.objects.all().delete()
        Image.objects.exclude(pk=self.page.image.pk).delete()

    def test_image_none(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 0)

    def test_image_not_in_collections(self):
        ImageFactory(collection=CollectionFactory(name='foo'))
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 0)

    def test_image_with_page(self):
        image_page = ImageFactory(collection=self.collections['page'])
        image_blog = ImageFactory(collection=self.collections['post'])

        basic_page = BasicPageFactory(parent=self.page, image=image_page)
        blog_page = BlogPageFactory(parent=self.page, image=image_blog)

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 2)

        images = {i.pk: i for i in response.context['images']}

        self.assertIn(image_page.pk, images)
        self.assertEqual(images[image_page.pk].page, basic_page)

        self.assertIn(image_blog.pk, images)
        self.assertEqual(images[image_blog.pk].page, blog_page)

    def test_image_without_page(self):
        image = ImageFactory(collection=self.collections['video'])

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 1)

        self.assertEqual(response.context['images'][0].pk, image.pk)
        self.assertIsNone(response.context['images'][0].page)

    def test_filter_collections(self):
        image = ImageFactory(collection=self.collections['post'])
        ImageFactory(collection=self.collections['video'])

        response = self.client.get(self.page.url, data={'collection': self.collections['post'].pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 1)

        self.assertEqual(response.context['images'][0].pk, image.pk)


class GalleryHTMLTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        CollectionFactory(name='Gallery')
        cls.page = GalleryPageFactory()

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = GalleryHTMLPage(response)

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
