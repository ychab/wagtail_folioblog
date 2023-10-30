from wagtail_factories import CollectionFactory

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.core.factories import ImageFactory
from folioblog.core.models import FolioBlogSettings
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase
from folioblog.gallery.factories import GalleryPageFactory
from folioblog.gallery.tests.selenium.webpages import GalleryWebPage


class GalleryPageLiveTestCase(FolioBlogSeleniumServerTestCase):
    def setUp(self):
        super().setUp()

        self.page = GalleryPageFactory(parent=self.site.root_page)
        self.index = BlogIndexPageFactory(parent=self.site.root_page)

        root_collection = CollectionFactory(name="Gallery")
        site_settings = FolioBlogSettings.for_site(self.site)
        site_settings.gallery_collection = root_collection
        site_settings.save()

        self.collection = CollectionFactory(name="Test", parent=root_collection)
        self.collection_alt = CollectionFactory(name="Alt test", parent=root_collection)

        self.images = [
            ImageFactory(collection=self.collection, file__width=480, file__height=360)
            for i in range(0, 3)
        ]
        self.images_alt = [
            ImageFactory(
                collection=self.collection_alt, file__width=480, file__height=360
            )
        ]
        self.image_orphan = [ImageFactory(file__width=480, file__height=360)]

        self.posts = []
        for img in self.images:
            self.posts.append(BlogPageFactory(parent=self.index, image=img))

        self.webpage = GalleryWebPage(self.selenium)
        self.webpage.fetch_page(self.page.full_url)

    def test_masthead_image(self):
        spec = "fill-1080x1380" if self.is_mobile else "fill-1905x560"
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())

    def test_layout_items(self):
        items = self.webpage.get_layout_items()
        self.assertEqual(len(items), len(self.images) + len(self.images_alt))

        post = self.posts[0]
        post_url = f"{self.live_server_url}{post.url}"
        spec = "fill-320x250" if self.is_mobile else "fill-468x351"
        rendition = post.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"

        # Order is random... Wouin, a do...while miss me!!
        item = items.pop(0)
        while item.get("title") != post.title:  # pragma: no cover
            item = items.pop(0)

        self.assertEqual(item["title"], post.title)
        self.assertEqual(item["href"], post_url)
        self.assertEqual(item["img_src"], rendition_url)

    def test_filter_collection(self):
        expected_count = len(self.images)
        is_filtered = self.webpage.filter_collection(self.collection.pk, expected_count)
        self.assertTrue(is_filtered)
        items = self.webpage.get_layout_items()
        self.assertEqual(len(items), expected_count)

        expected_count = len(self.images_alt)
        is_filtered = self.webpage.filter_collection(
            self.collection_alt.pk, expected_count
        )
        self.assertTrue(is_filtered)
        items = self.webpage.get_layout_items()
        self.assertEqual(len(items), len(self.images_alt))

    def test_check(self):
        is_scrolled = self.webpage.scroll_to_check()
        self.assertTrue(is_scrolled)

        is_checked = self.webpage.check()
        self.assertTrue(is_checked)

        self.webpage.scroll_to_top()

    def test_drag_drop_item(self):
        is_dragged = self.webpage.drag_and_drop()
        self.assertTrue(is_dragged)

    def test_resize_item(self):
        is_resized = self.webpage.resize_item()
        self.assertTrue(is_resized)
