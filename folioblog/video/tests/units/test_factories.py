from django.test import TestCase

from wagtail_factories import SiteFactory

from folioblog.home.factories import HomePageFactory
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory


class VideoPageFactoryTestCase(TestCase):
    def test_other_site(self):
        home = HomePageFactory(parent=None)
        site = SiteFactory(root_page=home)

        index = VideoIndexPageFactory(parent=home)
        page = VideoPageFactory(
            parent=index,
            tags__number=1,
            related_pages__number=1,
            promoted=True,
        )

        self.assertEqual(page.category.site, site)
        self.assertEqual(page.tags.first().site, site)
        self.assertEqual(page.related_links.first().related_page.get_site(), site)
        self.assertEqual(page.promoted_links.first().snippet.site, site)
