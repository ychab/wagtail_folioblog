from django.test import TestCase

import requests
import requests_mock
from wagtail_factories import CollectionFactory

from folioblog.core.factories import ImageFactory
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory
from folioblog.video.models import VideoPage


class VideoPageModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.collection = CollectionFactory(name="Video thumbnail")
        cls.index = VideoIndexPageFactory()

    def tearDown(self):
        VideoPage.objects.all().delete()

    def test_embed_succeed(self):
        page = VideoPageFactory(parent=self.index, embed__skip=True)
        self.assertTrue(page.embed)
        self.assertTrue(page.embed.width)
        self.assertTrue(page.embed.height)
        self.assertTrue(page.embed.thumbnail_url)

    def test_embed_failed(self):
        page = VideoPageFactory(
            parent=self.index,
            embed__skip=True,
            video_url="https://www.youtube.com/watch?v=FOO",
        )
        with self.assertLogs("folioblog.video.models", level="ERROR") as cm:
            page.embed
        self.assertIn("Embed error for page", cm.output[0])

    def test_thumbnail_already_exists(self):
        image = ImageFactory()
        page = VideoPageFactory(parent=self.index, embed__skip=True, thumbnail=image)
        page.save_revision()
        self.assertEqual(page.thumbnail, image)

    @requests_mock.Mocker()
    def test_thumbnail_request_exception(self, m):
        page = VideoPageFactory(parent=self.index, embed__skip=True, thumbnail=None)
        m.get(page.embed.thumbnail_url, exc=requests.exceptions.HTTPError)

        with self.assertLogs("folioblog.video.models", level="ERROR") as cm:
            page.save_revision()
        self.assertIn("Error thumbnail", cm.output[0])
        self.assertFalse(page.thumbnail)

    @requests_mock.Mocker()
    def test_thumbnail_request_bad_status(self, m):
        page = VideoPageFactory(parent=self.index, embed__skip=True, thumbnail=None)
        m.get(page.embed.thumbnail_url, status_code=400)

        with self.assertLogs("folioblog.video.models", level="WARNING") as cm:
            page.save_revision()
        self.assertIn("Bad status", cm.output[0])
        self.assertFalse(page.thumbnail)

    def test_thumbnail_attach(self):
        page = VideoPageFactory(parent=self.index, embed__skip=True, thumbnail=None)
        page.save_revision()
        self.assertTrue(page.thumbnail)
