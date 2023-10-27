from folioblog.core.factories import ImageFactory
from folioblog.core.tests.selenium.webpages import NotFoundWebPage
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase
from folioblog.home.factories import HomePageFactory


class NotFoundPageLiveTestCase(FolioBlogSeleniumServerTestCase):
    def setUp(self):
        super().setUp()

        HomePageFactory(parent=self.site.root_page)
        self.image_bg = ImageFactory(title="404-bg")

        url = f"{self.live_server_url}/givemea404please"
        self.webpage = NotFoundWebPage(self.selenium)
        self.webpage.fetch_page(url, skip_check_url=True, force_consent=False)

    def test_masthead_image(self):
        spec = "fill-1080x1380" if self.is_mobile else "fill-1905x560"
        rendition = self.image_bg.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())
