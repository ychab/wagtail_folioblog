from folioblog.core.factories import BasicPageFactory
from folioblog.core.tests.selenium.webpages import BasicWebPage
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase, skip_mobile


class BasicPageLiveTestCase(FolioBlogSeleniumServerTestCase):
    def setUp(self):
        super().setUp()

        self.page = BasicPageFactory(
            parent=self.site.root_page, related_pages__number=1
        )

        self.webpage = BasicWebPage(self.selenium)
        self.webpage.fetch_page(self.page.full_url)

    @skip_mobile()
    def test_title(self):
        return self.assertEqual(self.page.title, self.webpage.title)

    def test_masthead_image(self):
        spec = "fill-1080x1380" if self.is_mobile else "fill-1905x560"
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())

    def test_image(self):
        data = self.webpage.get_image_with_caption()
        spec = "width-940" if self.is_mobile else "width-700"
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        self.assertEqual(rendition_url, data["img_src"])
        self.assertIn(self.page.caption, data["caption"])
        self.assertIn(str(self.page.image.photographer), data["caption"])

    def test_related_page(self):
        data = self.webpage.get_related_pages()
        page_related = self.page.related_links.first().related_page.specific
        page_related_url = f"{self.live_server_url}{page_related.url}"
        spec = "fill-150x150"  # No mobile profile yet
        rendition = page_related.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"

        self.assertEqual(data[0]["title"], page_related.title)
        self.assertEqual(data[0]["url"], page_related_url)
        self.assertEqual(data[0]["img_src"], rendition_url)
