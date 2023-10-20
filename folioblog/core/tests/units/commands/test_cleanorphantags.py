from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from taggit.models import Tag

from folioblog.blog.factories import (
    BlogIndexPageFactory,
    BlogPageFactory,
    BlogTagFactory,
)
from folioblog.blog.models import BlogTag
from folioblog.core.factories import ImageFactory, TagFactory
from folioblog.video.factories import (
    VideoIndexPageFactory,
    VideoPageFactory,
    VideoTagFactory,
)
from folioblog.video.models import VideoTag


class CleanOrphanTagsCommandTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_index = BlogIndexPageFactory()
        cls.video_index = VideoIndexPageFactory()

    def tearDown(self):
        Tag.objects.all().delete()
        BlogTag.objects.all().delete()
        VideoTag.objects.all().delete()

    def test_tag_used(self):
        tag = TagFactory()
        ImageFactory(tags=[tag])

        out = StringIO()
        call_command("cleanorphantags", stdout=out)
        self.assertIn("0 orphan tags deleted", out.getvalue())

    def test_tag_orphan(self):
        TagFactory()

        out = StringIO()
        call_command("cleanorphantags", stdout=out)
        self.assertIn("1 orphan tags deleted", out.getvalue())

    def test_blogtag_used(self):
        tag = BlogTagFactory()
        BlogPageFactory(parent=self.post_index, tags=[tag])

        out = StringIO()
        call_command("cleanorphantags", stdout=out)
        self.assertIn("0 orphan tags deleted", out.getvalue())

    def test_blogtag_orphan(self):
        BlogTagFactory()

        out = StringIO()
        call_command("cleanorphantags", stdout=out)
        self.assertIn("1 orphan tags deleted", out.getvalue())

    def test_videotag_used(self):
        tag = VideoTagFactory()
        VideoPageFactory(parent=self.video_index, tags=[tag])

        out = StringIO()
        call_command("cleanorphantags", stdout=out)
        self.assertIn("0 orphan tags deleted", out.getvalue())

    def test_videotag_orphan(self):
        VideoTagFactory()

        out = StringIO()
        call_command("cleanorphantags", stdout=out)
        self.assertIn("1 orphan tags deleted", out.getvalue())
