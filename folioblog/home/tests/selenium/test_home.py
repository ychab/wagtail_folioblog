from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase, skip_mobile
from folioblog.home.factories import HomePageFactory
from folioblog.home.tests.selenium.webpages import HomeWebPage
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory


class HomePageLiveTestCase(FolioBlogSeleniumServerTestCase):
    def setUp(self):
        super().setUp()

        self.page = HomePageFactory(parent=self.site.root_page)
        self.index_post = BlogIndexPageFactory(parent=self.site.root_page)
        self.index_video = VideoIndexPageFactory(parent=self.site.root_page)

        self.posts = []
        self.limit_posts = 5
        for i in range(0, self.limit_posts):
            self.posts.append(BlogPageFactory(parent=self.index_post, promoted=True))

        self.videos = []
        self.limit_videos = 5
        for i in range(0, self.limit_videos):
            self.videos.append(VideoPageFactory(parent=self.index_video, promoted=True))

        self.webpage = HomeWebPage(self.selenium)
        self.webpage.fetch_page(self.page.full_url)

    def test_masthead_image(self):
        spec = "fill-1080x1380" if self.is_mobile else "fill-1905x560"
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f"{self.live_server_url}{rendition.url}"
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())

    @skip_mobile("@fixme - action drag_n_drop() is broken on mobile!?")
    def test_carousel_posts_dragdrop_next(self):
        self.webpage.scroll_to_carousel_post()
        self.webpage.promoted_posts_dragdrop()
        self.assertTrue(self.webpage.is_last_slide(len(self.posts)))

    def test_carousel_posts_click_next(self):
        self.webpage.scroll_to_carousel_post()
        self.webpage.promoted_posts_next()
        self.assertTrue(self.webpage.is_last_slide(len(self.posts)))
        self.webpage.scroll_to_top()

    def test_video_play_first(self):
        is_scrolled = self.webpage.scroll_to_carousel_videos()
        self.assertTrue(is_scrolled)

        is_triggered, is_loaded = self.webpage.play_video()
        self.assertTrue(is_triggered)

        if is_loaded:  # pragma: no cover
            is_stopped = self.webpage.stop_video()
            self.assertTrue(is_stopped)

        self.webpage.scroll_to_top()

    def test_video_play_second(self):
        is_scrolled = self.webpage.scroll_to_carousel_videos()
        self.assertTrue(is_scrolled)

        is_selected = self.webpage.select_video(2, self.is_mobile)
        self.assertTrue(is_selected)
        is_triggered, is_loaded = self.webpage.play_video()
        self.assertTrue(is_triggered)

        if is_loaded:  # pragma: no cover
            is_stopped = self.webpage.stop_video()
            self.assertTrue(is_stopped)

        self.webpage.scroll_to_top()

    def test_video_play_both(self):
        is_scrolled = self.webpage.scroll_to_carousel_videos()
        self.assertTrue(is_scrolled)

        is_triggered, is_loaded = self.webpage.play_video()
        self.assertTrue(is_triggered)

        # Enabling player change viewport position!? Why??
        is_scrolled = self.webpage.scroll_to_carousel_videos()
        self.assertTrue(is_scrolled)

        is_triggered, is_loaded = self.webpage.play_video_of(2)
        self.assertTrue(is_triggered)

        if is_loaded:  # pragma: no cover
            is_stopped = self.webpage.stop_videos()
            self.assertTrue(is_stopped)

        self.webpage.scroll_to_top()
