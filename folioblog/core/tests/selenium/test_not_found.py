from folioblog.core.factories import ImageFactory
from folioblog.core.models import FolioBlogSettings
from folioblog.core.tests.selenium.webpages import NotFoundWebPage
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase


class NotFoundPageLiveTestCase(FolioBlogSeleniumServerTestCase):
    def setUp(self):
        super().setUp()

        self.image_bg = ImageFactory()

        self.foliosettings = FolioBlogSettings.for_site(self.site)
        self.foliosettings.image_404 = self.image_bg
        self.foliosettings.save()

        url = f"{self.live_server_url}/givemea404please"
        self.webpage = NotFoundWebPage(self.selenium)
        self.webpage.fetch_page(url, skip_check_url=True, force_consent=False)

    def test_masthead_image(self):
        spec = "fill-1080x1380" if self.is_mobile else "fill-1905x560"
        rendition = self.image_bg.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())
