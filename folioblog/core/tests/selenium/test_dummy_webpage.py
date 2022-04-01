import os
import tempfile

from folioblog.core.factories import BasicPageFactory
from folioblog.core.tests.selenium.webpages.dummy_page import DummyWebPage
from folioblog.core.utils.tests import (
    FolioBlogSeleniumServerTestCase, skip_mobile,
)


class ScreenShotLiveTestCase(FolioBlogSeleniumServerTestCase):

    def setUp(self):
        super().setUp()

        self.page = BasicPageFactory(parent=self.site.root_page)
        self.url = f'{self.live_server_url}{self.page.url}'
        self.screenshot_dir = tempfile.mkdtemp(prefix='folioblog-', suffix='-test')

        self.webpage = DummyWebPage(self.selenium)
        self.webpage.fetch_page(self.url)

    @staticmethod
    def get_screenshot_files(dir):
        return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    @skip_mobile()
    def test_screenshot(self):
        saved = self.webpage.save_screenshot(self.screenshot_dir, 'foo')
        self.assertTrue(saved)

        files = self.get_screenshot_files(self.screenshot_dir)
        self.assertEqual(len(files), 1)
