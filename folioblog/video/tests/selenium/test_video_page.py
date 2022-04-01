from selenium.common import TimeoutException

from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory
from folioblog.video.tests.selenium.webpages import VideoWebPage


class VideoPageLiveTestCase(FolioBlogSeleniumServerTestCase):

    def setUp(self):
        super().setUp()

        self.index = VideoIndexPageFactory(parent=self.site.root_page)
        self.page = VideoPageFactory(parent=self.index, tags__number=2, related_pages__number=1)

        self.webpage = VideoWebPage(self.selenium)
        self.webpage.fetch_page(f'{self.live_server_url}{self.page.url}')
        self.webpage.cookies_accept()

    def test_masthead_image(self):
        spec = 'fill-1080x1380' if self.is_mobile else 'fill-1905x560'
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f'{self.live_server_url}{rendition.url}'
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())

    def test_play_video(self):
        is_clickable = self.webpage.scroll_to_video()
        self.assertTrue(is_clickable)

        is_triggered, is_loaded = self.webpage.play_video()
        self.assertTrue(is_triggered)

        if is_loaded:  # pragma: no cover
            is_stopped = self.webpage.stop_video()
            self.assertTrue(is_stopped)

        self.webpage.scroll_to_top()

    def test_related_page(self):
        data = self.webpage.get_related_pages()
        page_related = self.page.related_links.first().related_page.specific
        page_related_url = f'{self.live_server_url}{page_related.url}'
        spec = 'fill-150x150'  # No mobile profile yet
        rendition = page_related.image.get_rendition(spec)
        rendition_url = f'{self.live_server_url}{rendition.url}'

        self.assertEqual(data[0]['title'], page_related.title)
        self.assertEqual(data[0]['url'], page_related_url)
        self.assertEqual(data[0]['img_src'], rendition_url)


class CookieBannerVideoPageLiveTestCase(FolioBlogSeleniumServerTestCase):

    def setUp(self):
        super().setUp()

        self.index = VideoIndexPageFactory(parent=self.site.root_page)
        self.page = VideoPageFactory(parent=self.index)

        self.webpage = VideoWebPage(self.selenium)
        self.webpage.fetch_page(f'{self.live_server_url}{self.page.url}')

    def tearDown(self):
        self.webpage.cookie_consent_reset()

    def test_reject_cookie(self):
        self.webpage.cookies_reject()

        is_clickable = self.webpage.scroll_to_video()
        self.assertTrue(is_clickable)

        has_consent_banner = self.webpage.has_cookie_consent_banner()
        self.assertTrue(has_consent_banner)

        with self.assertRaises(TimeoutException):
            self.webpage.play_video()

        self.webpage.scroll_to_top()

    def test_accept_cookie(self):
        self.webpage.cookies_accept()

        is_clickable = self.webpage.scroll_to_video()
        self.assertTrue(is_clickable)

        with self.assertRaises(TimeoutException):
            self.webpage.has_cookie_consent_banner()

        is_triggered, is_loaded = self.webpage.play_video()
        self.assertTrue(is_triggered)

        self.webpage.scroll_to_top()
