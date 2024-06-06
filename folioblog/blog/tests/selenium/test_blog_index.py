from django.conf import settings
from django.utils import translation
from django.utils.formats import date_format
from django.utils.translation import gettext

from folioblog.blog.factories import (
    BlogCategoryFactory,
    BlogIndexPageFactory,
    BlogPageFactory,
)
from folioblog.blog.tests.selenium.webpages import BlogIndexWebPage
from folioblog.core.models import FolioBlogSettings
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase


class BlogIndexPageLiveTestCase(FolioBlogSeleniumServerTestCase):
    def setUp(self):
        super().setUp()

        self.foliosettings = FolioBlogSettings.for_site(self.site)

        self.categories = [
            BlogCategoryFactory(name="Tech"),
            BlogCategoryFactory(name="Économie"),
            BlogCategoryFactory(name="Philosophie"),
        ]
        self.page = BlogIndexPageFactory(parent=self.site.root_page)
        self.posts = []
        limit = (self.foliosettings.blog_pager_limit * 2) + 1
        for i in range(0, limit):
            category = self.categories[0] if i + 1 < limit else self.categories[1]
            self.posts.append(BlogPageFactory(parent=self.page, category=category))

        self.webpage = BlogIndexWebPage(self.selenium)
        self.webpage.fetch_page(self.page.full_url)
        self.webpage.set_language("fr")

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_masthead_image(self):
        spec = "fill-1080x1380" if self.is_mobile else "fill-1905x560"
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())

    def test_grid_item(self):
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), self.foliosettings.blog_pager_limit)

        item = items[0]
        post = self.posts[-1]

        post_url = f"{self.live_server_url}{post.url}"
        spec = "fill-1010x675" if self.is_mobile else "fill-460x310"
        rendition = post.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        page_date = "{} {}".format(gettext("Publié le"), date_format(post.date, "SHORT_DATE_FORMAT"))

        self.assertEqual(item["title"], self.posts[-1].title)
        self.assertEqual(item["link"], post_url)
        self.assertEqual(item["date"], page_date)
        self.assertEqual(item["intro"], post.intro)
        self.assertEqual(item["img_src"], rendition_url)

    def test_infinite_scroll(self):
        expected_count = self.foliosettings.blog_pager_limit * 2
        is_scrolled = self.webpage.scroll_down(expected_count)
        self.assertTrue(is_scrolled)
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), expected_count)

        expected_count = (self.foliosettings.blog_pager_limit * 2) + 1
        is_scrolled = self.webpage.scroll_down(expected_count)
        self.assertTrue(is_scrolled)
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), expected_count)
        self.assertEqual(len(items), len(self.posts))
        self.assertIn("Oh non, c'est déjà fini !!", self.webpage.content)
        self.webpage.scroll_to_top()

    def test_categories_filter(self):
        category = self.categories[1]

        expected_count = 1
        is_filtered = self.webpage.filter_category(category.slug, expected_count)
        self.assertTrue(is_filtered)

        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(category.name, items[0]["category"])

    def test_categories_filter_and_scroll(self):
        category = self.categories[0]

        expected_count = self.foliosettings.blog_pager_limit
        is_filtered = self.webpage.filter_category(category.slug, expected_count)
        items = self.webpage.get_grid_items()
        self.assertTrue(is_filtered)
        self.assertEqual(len(items), expected_count)

        categories = list(set([i["category"] for i in items]))
        self.assertEqual(len(categories), 1)
        self.assertEqual(category.name, categories[0])

        expected_count = self.foliosettings.blog_pager_limit * 2
        is_scrolled = self.webpage.scroll_down(expected_count)
        self.assertTrue(is_scrolled)
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), expected_count)

        categories = list(set([i["category"] for i in items]))
        self.assertEqual(len(categories), 1)
        self.assertEqual(category.name, categories[0])

        self.assertIn("Oh non, c'est déjà fini !!", self.webpage.content)
        self.webpage.scroll_to_top()
