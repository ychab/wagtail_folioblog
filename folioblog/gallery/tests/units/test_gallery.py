from django.conf import settings
from django.test import TestCase

from wagtail.images import get_image_model
from wagtail.models import Site

from wagtail_factories import CollectionFactory, SiteFactory

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.blog.models import BlogPage
from folioblog.core.factories import BasicPageFactory, ImageFactory, LocaleFactory
from folioblog.core.models import BasicPage, FolioBlogSettings
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.core.utils.tests.units import MultiDomainPageTestCase
from folioblog.gallery.factories import GalleryPageFactory
from folioblog.gallery.tests.units.htmlpages import GalleryHTMLPage
from folioblog.home.factories import HomePageFactory

Image = get_image_model()


class GalleryPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        root_collection = CollectionFactory(name="Gallery")

        cls.site = Site.objects.get(is_default_site=True)
        site_settings = FolioBlogSettings.for_site(cls.site)
        site_settings.gallery_collection = root_collection
        site_settings.save()

        cls.collections = {}
        for name in ["page", "post", "video"]:
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
        self.assertEqual(len(response.context["images"]), 0)

    def test_image_not_in_collections(self):
        ImageFactory(collection=CollectionFactory(name="foo"))
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["images"]), 0)

    def test_image_without_page(self):
        image = ImageFactory(collection=self.collections["video"])

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["images"]), 1)

        self.assertEqual(response.context["images"][0].pk, image.pk)
        self.assertIsNone(response.context["images"][0].page)

    def test_image_with_page(self):
        image_page = ImageFactory(collection=self.collections["page"])
        image_blog = ImageFactory(collection=self.collections["post"])

        basic_page = BasicPageFactory(parent=self.page, image=image_page)
        blog_page = BlogPageFactory(parent=self.page, image=image_blog)

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["images"]), 2)
        images = {i.pk: i for i in response.context["images"]}

        self.assertIn(image_page.pk, images)
        self.assertEqual(images[image_page.pk].page, basic_page)

        self.assertIn(image_blog.pk, images)
        self.assertEqual(images[image_blog.pk].page, blog_page)

    def test_image_in_richtext_i18n(self):
        image_main = ImageFactory(collection=self.collections["post"])
        image_body = ImageFactory(collection=self.collections["post"])

        blog_page = BlogPageFactory(
            parent=self.page,
            image=image_main,
            body=f'<embed alt="Foo Bar Baz" embedtype="image" format="bodyfullfuild" id="{image_body.pk}"/>',
        )
        blog_page.copy_for_translation(
            locale=LocaleFactory(language_code="en"),
            copy_parents=True,
        )

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["images"]), 2)
        images = {i.pk: i for i in response.context["images"]}

        self.assertIn(image_main.pk, images)
        self.assertEqual(images[image_main.pk].page, blog_page)

        self.assertIn(image_body.pk, images)
        self.assertEqual(images[image_body.pk].page, blog_page)

    def test_filter_exclude_collections(self):
        image = ImageFactory(collection=self.collections["post"])
        ImageFactory(collection=CollectionFactory())

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["images"]), 1)

        self.assertEqual(response.context["images"][0].pk, image.pk)

    def test_filter_collections(self):
        image = ImageFactory(collection=self.collections["post"])
        ImageFactory(collection=self.collections["video"])

        response = self.client.get(
            self.page.url, data={"collection": self.collections["post"].pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["images"]), 1)

        self.assertEqual(response.context["images"][0].pk, image.pk)


class GalleryPageNoSettingsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page = GalleryPageFactory()

    def tearDown(self):
        Image.objects.exclude(pk=self.page.image.pk).delete()

    def test_no_collections(self):
        image = ImageFactory()

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(image.pk, [i.pk for i in response.context["images"]])


class GalleryPageMultiDomainTestCase(MultiDomainPageTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = HomePageFactory(slug="home")
        cls.site = Site.objects.get(is_default_site=True)
        cls.gallery = GalleryPageFactory(parent=cls.root_page)
        cls.index = BlogIndexPageFactory(parent=cls.root_page)
        cls.blog = BlogPageFactory(parent=cls.index)

        cls.home_other = HomePageFactory(slug="home_other")
        cls.site_other = SiteFactory(root_page=cls.home_other)
        cls.gallery_other = GalleryPageFactory(parent=cls.home_other)
        cls.index_other = BlogIndexPageFactory(parent=cls.home_other)
        cls.blog_other = BlogPageFactory(parent=cls.index_other)

        super().setUpTestData()

    def test_filter_site(self):
        response = self.client.get(self.gallery.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn(
            self.blog.pk,
            [i.page.pk for i in response.context["images"] if getattr(i, "page")],
        )
        self.assertNotIn(
            self.blog_other.pk,
            [i.page.pk for i in response.context["images"] if getattr(i, "page")],
        )


class GalleryHTMLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        root_collection = CollectionFactory(name="Gallery")

        cls.site = Site.objects.get(is_default_site=True)
        site_settings = FolioBlogSettings.for_site(cls.site)
        site_settings.gallery_collection = root_collection
        site_settings.save()

        cls.page = GalleryPageFactory()

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = GalleryHTMLPage(response)

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


class GalleryHTMLi18nTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        root_collection = CollectionFactory(name="Gallery")

        cls.site = Site.objects.get(is_default_site=True)
        site_settings = FolioBlogSettings.for_site(cls.site)
        site_settings.gallery_collection = root_collection
        site_settings.save()

        cls.page_fr = GalleryPageFactory(
            locale=LocaleFactory(language_code="fr"),
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=LocaleFactory(language_code="en"),
            copy_parents=True,
            alias=True,
        )

    def test_lang_default(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = GalleryHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), settings.LANGUAGE_CODE)

    def test_lang_fr(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = GalleryHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_fr.locale.language_code)

    def test_lang_en(self):
        response = self.client.get(self.page_en.url)
        htmlpage = GalleryHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_en.locale.language_code)

    def test_alternates(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = GalleryHTMLPage(response)

        self.assertListEqual(
            sorted(htmlpage.get_meta_alternates()),
            sorted([page.full_url for page in [self.page_fr, self.page_en]]),
        )
