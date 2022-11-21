from django.test import override_settings

from folioblog.core.models import FolioBlogSettings
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase
from folioblog.video.factories import (
    VideoCategoryFactory, VideoIndexPageFactory, VideoPageFactory,
)
from folioblog.video.tests.selenium.webpages import VideoIndexWebPage


class VideoIndexPageLiveTestCase(FolioBlogSeleniumServerTestCase):

    def setUp(self):
        super().setUp()

        self.categories = [
            VideoCategoryFactory(name='Humour'),
            VideoCategoryFactory(name='Cinéma'),
            VideoCategoryFactory(name='Tutoriel'),
        ]

        self.page = VideoIndexPageFactory(parent=self.site.root_page)

        # Be sure to ALWAYS have DIFFERENT video ID in the page
        youtube_urls = [
            'https://www.youtube.com/watch?v=OeXFD1Aps1g',
            'https://www.youtube.com/watch?v=FW1zNwKQ8Sw',
            'https://www.youtube.com/watch?v=Z0JHTUSDGNg',
            'https://www.youtube.com/watch?v=KLOn3i-mah4',
            'https://www.youtube.com/watch?v=ml9ahwz_oNA',
        ]
        self.foliosettings = FolioBlogSettings.load()
        self.foliosettings.video_pager_limit = round((len(youtube_urls) / 2) - 1)  # we got at least 2 pages
        self.foliosettings.save()

        self.videos = []
        for i, video_url in enumerate(youtube_urls, start=1):
            category = self.categories[0] if i < len(youtube_urls) else self.categories[1]
            self.videos.append(VideoPageFactory(
                parent=self.page,
                category=category,
                video_url=video_url,
            ))

        self.webpage = VideoIndexWebPage(self.selenium)
        self.webpage.fetch_page(self.page.full_url)

    def test_masthead_image(self):
        spec = 'fill-1080x1380' if self.is_mobile else 'fill-1905x560'
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f'{self.live_server_url}{rendition.url}'
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())

    def test_grid_item(self):
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), self.foliosettings.video_pager_limit)

        item = items[0]
        video = self.videos[-1]

        video_url = f'{self.live_server_url}{video.url}'
        spec = 'fill-940x710|format-webp' if self.is_mobile else 'fill-700x530|format-webp'
        rendition = video.thumbnail.get_rendition(spec)
        rendition_url = f'{self.live_server_url}{rendition.url}'

        self.assertEqual(item['title'], video.title)
        self.assertEqual(item['subtitle'], video.subheading)
        self.assertEqual(item['link'], video_url)
        self.assertEqual(item['intro'], video.intro)
        self.assertEqual(item['img_src'], rendition_url)
        self.assertEqual(item['category'], str(video.category))
        self.assertEqual(item['tags'], ' '.join([t.name for t in video.tags.all()]))

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_infinite_scroll(self):
        expected_count = self.foliosettings.video_pager_limit * 2
        is_scrolled = self.webpage.scroll_down(expected_count)
        self.assertTrue(is_scrolled)
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), expected_count)

        expected_count = (self.foliosettings.video_pager_limit * 2) + 1
        is_scrolled = self.webpage.scroll_down(expected_count)
        self.assertTrue(is_scrolled)
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), expected_count)
        self.assertEqual(len(items), len(self.videos))
        self.assertIn("Oh non, c'est déjà fini !!", self.webpage.content)
        self.webpage.scroll_to_top()

    def test_categories_filter(self):
        category = self.categories[1]

        expected_count = 1
        is_filtered = self.webpage.filter_category(category.slug, expected_count)
        self.assertTrue(is_filtered)

        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(category.name, items[0]['category'])

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_categories_filter_and_scroll(self):
        category = self.categories[0]

        expected_count = self.foliosettings.video_pager_limit
        is_filtered = self.webpage.filter_category(category.slug, expected_count)
        self.assertTrue(is_filtered)
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), expected_count)

        categories = list(set([i['category'] for i in items]))
        self.assertEqual(len(categories), 1)
        self.assertEqual(category.name, categories[0])

        expected_count = self.foliosettings.video_pager_limit * 2
        is_scrolled = self.webpage.scroll_down(expected_count)
        self.assertTrue(is_scrolled)
        items = self.webpage.get_grid_items()
        self.assertEqual(len(items), expected_count)

        categories = list(set([i['category'] for i in items]))
        self.assertEqual(len(categories), 1)
        self.assertEqual(category.name, categories[0])

        self.assertIn("Oh non, c'est déjà fini !!", self.webpage.content)
        self.webpage.scroll_to_top()

    def test_play_videos(self):
        index = 1
        is_clickable = self.webpage.scroll_to_video(index)
        self.assertTrue(is_clickable)
        is_played = self.webpage.play_video(index)
        self.assertTrue(is_played)
        is_stopped = self.webpage.stop_video(index)
        self.assertTrue(is_stopped)

        index = 2
        is_clickable = self.webpage.scroll_to_video(index)
        self.assertTrue(is_clickable)
        is_played = self.webpage.play_video(index)
        self.assertTrue(is_played)
        is_stopped = self.webpage.stop_video(index)
        self.assertTrue(is_stopped)

    def test_filter_and_play_videos(self):
        category = self.categories[0]

        expected_count = self.foliosettings.video_pager_limit
        is_filtered = self.webpage.filter_category(category.slug, expected_count)
        self.assertTrue(is_filtered)

        index = 1
        is_clickable = self.webpage.scroll_to_video(index)
        self.assertTrue(is_clickable)
        is_played = self.webpage.play_video(index)
        self.assertTrue(is_played)
