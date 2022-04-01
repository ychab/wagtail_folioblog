from folioblog.core.factories import BasicPageFactory
from folioblog.core.tests.selenium.webpages import BasicWebPage
from folioblog.core.utils.tests import (
    FolioBlogSeleniumServerTestCase, skip_mobile,
)


class CookieBannerLiveTestCase(FolioBlogSeleniumServerTestCase):

    def setUp(self):
        super().setUp()

        self.page = BasicPageFactory(parent=self.site.root_page)
        self.url = f'{self.live_server_url}{self.page.url}'
        self.webpage = BasicWebPage(self.selenium)
        self.webpage.fetch_page(self.url)

    def tearDown(self):
        self.webpage.cookie_consent_reset()

    @skip_mobile()
    def test_cookie_reset(self):
        self.webpage.force_cookie_consent()
        self.webpage.cookie_consent_reset()
        self.assertIsNone(self.webpage.has_cookie_consent())

    def test_cookie_accept(self):
        is_disappeared = self.webpage.cookies_accept()
        self.assertTrue(is_disappeared)
        self.assertTrue(self.webpage.has_cookie_consent())

    @skip_mobile()
    def test_cookie_already_accepted(self):
        self.webpage.force_cookie_consent()
        self.assertTrue(self.webpage.has_cookie_consent())

        self.webpage.cookies_accept()
        self.assertTrue(self.webpage.has_cookie_consent())

    def test_cookie_reject(self):
        is_disappeared = self.webpage.cookies_reject()
        self.assertTrue(is_disappeared)
        self.assertFalse(self.webpage.has_cookie_consent())

    @skip_mobile()
    def test_cookie_already_rejected(self):
        self.webpage.force_cookie_consent(value='false')
        self.assertFalse(self.webpage.has_cookie_consent())

        self.webpage.cookies_reject()
        self.assertFalse(self.webpage.has_cookie_consent())

    @skip_mobile()
    def test_banner_visible_noconsent(self):
        self.assertTrue(self.webpage.has_cookie_banner())

    @skip_mobile()
    def test_banner_invisible_consent(self):
        self.webpage.force_cookie_consent()
        self.webpage.fetch_page(self.url)
        self.assertFalse(self.webpage.has_cookie_banner())

    @skip_mobile()
    def test_banner_invisible_rejected(self):
        self.webpage.force_cookie_consent(value='false')
        self.webpage.fetch_page(self.url)
        self.assertFalse(self.webpage.has_cookie_banner())
